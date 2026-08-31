#!/usr/bin/env python3
"""
Fetch the Artificial Minds numbers from GoatCounter and write stats/data.json.

Run it with the API token in the environment:

    GOATCOUNTER_TOKEN=... python3 scripts/fetch_stats.py

The script calls the API one request at a time, builds the whole file in memory,
and writes stats/data.json only after every call has succeeded. If anything goes
wrong it leaves the old file exactly as it was and exits with a nonzero status,
so the GitHub Action shows a failure instead of publishing half a file.

Two things about the numbers are worth knowing.

First, the GoatCounter statistics API counts visits, not pageviews. Since
GoatCounter 2.0 the hourly totals it keeps only count the first pageview of each
session, so every number the /api/v0/stats/... endpoints return is a visitor
count. The one place a real pageview count exists is the CSV export, which lists
every individual pageview. This script downloads that export when it can and
uses it for the "views" fields. The export only works if "Individual pageviews"
is switched on in the GoatCounter site settings, and it can only be started once
an hour. When it is not available the views fields fall back to the visitor
counts and the script prints a warning. Set GOATCOUNTER_SKIP_EXPORT=1 to skip
the export step entirely.

Second, all-time counters never go down. GoatCounter's own data can age out, so
the script keeps the previous file's monthly history and takes the larger of the
old and the new value for every all-time counter.
"""

import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# Where the numbers come from. The site code is "artificialminds", so the base
# is the hosted GoatCounter subdomain for that code.
API_BASE = os.environ.get(
    "GOATCOUNTER_API_BASE", "https://artificialminds.goatcounter.com/api/v0"
)

# The site is served under this path prefix on GitHub Pages, so recorded paths
# look like "/artificialminds/stillpoint/index.html". The prefix is stripped
# before anything is classified or written out.
SITE_PREFIX = "/artificialminds"

# The five projects, in the order the dashboard shows them. The id is the folder
# name in the repo, which is also the first path segment after the prefix.
PROJECTS = [
    ("can-artificial-minds-feel", "Can Artificial Minds Feel?"),
    ("A-Salon-of-Witnesses", "A Salon of Witnesses"),
    ("artificial-mind-of-your-own", "An Artificial Mind of Your Own"),
    ("AI-future-canon", "AI Future Canon"),
    ("stillpoint", "Stillpoint"),
]
HOME_ID = "home"
HOME_NAME = "Home"

DAILY_DAYS = 90          # length of the day by day series
SUMMARY_DAYS = 30        # window for every "last 30 days" number

# Far enough back that it covers everything GoatCounter still holds. GoatCounter
# itself did not exist before 2019, so nothing can be older than this.
ALL_TIME_START = "2019-01-01T00:00:00Z"

# The API allows four requests a second. One request every third of a second
# stays well under that, and every call is made one after the other.
MIN_SECONDS_BETWEEN_CALLS = 0.3
REQUEST_TIMEOUT = 90
RETRIES = 3

# How long to wait for GoatCounter to finish building a CSV export.
EXPORT_POLL_SECONDS = 3
EXPORT_MAX_WAIT_SECONDS = 180

# GoatCounter groups screen widths into five buckets and returns only the bucket
# id, with an empty name. These are the widths behind each bucket.
SIZE_NAMES = {
    "phone": "Phone",            # up to 600 pixels wide
    "tablet": "Tablet",          # 601 to 1000
    "desktop": "Desktop",        # 1001 to 1920
    "desktophd": "Large screen",  # wider than 1920
    "unknown": "Unknown",        # no screen size was reported
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(REPO_ROOT, "stats", "data.json")


class FetchError(Exception):
    """A call failed. The old data.json stays where it is and the run fails."""


# ----------------------------------------------------------------------------
# Talking to the API
# ----------------------------------------------------------------------------

_last_call_at = [0.0]


def _throttle():
    """Keep a gap between calls so we stay under four requests a second."""
    gap = MIN_SECONDS_BETWEEN_CALLS - (time.monotonic() - _last_call_at[0])
    if gap > 0:
        time.sleep(gap)
    _last_call_at[0] = time.monotonic()


def _build_request(method, url, token, body=None):
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method=method)
    request.add_header("Authorization", "Bearer " + token)
    request.add_header("Content-Type", "application/json")
    request.add_header("User-Agent", "artificialminds-stats/1.0")
    return request


def _error_detail(err):
    """Pull a readable message out of an error response."""
    try:
        raw = err.read().decode("utf-8", "replace")
    except Exception:
        return err.reason if err.reason else "no detail"
    try:
        parsed = json.loads(raw)
    except ValueError:
        return raw.strip()[:300] or "no detail"
    if isinstance(parsed, dict):
        if parsed.get("error"):
            return str(parsed["error"])
        if parsed.get("errors"):
            return json.dumps(parsed["errors"])
    return raw.strip()[:300]


def _retry_wait(err, attempt):
    """Wait as long as the rate limit header asks, or back off a little."""
    reset = err.headers.get("X-Rate-Limit-Reset") if err.headers else None
    if reset:
        try:
            return min(30, max(1, int(reset)))
        except ValueError:
            pass
    return 2 ** attempt


def api_call(method, path, token, params=None, body=None):
    """Make one API call and return the decoded JSON."""
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    last_problem = "unknown"
    for attempt in range(RETRIES):
        _throttle()
        try:
            with urllib.request.urlopen(
                _build_request(method, url, token, body), timeout=REQUEST_TIMEOUT
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as err:
            detail = _error_detail(err)
            # 429 means we went past the rate limit and 5xx means GoatCounter is
            # having a bad moment. Both are worth another try. Everything else,
            # a bad token above all, will not get better by asking again.
            if err.code == 429 or err.code >= 500:
                last_problem = "HTTP %d (%s)" % (err.code, detail)
                time.sleep(_retry_wait(err, attempt))
                continue
            raise FetchError(
                "%s %s failed with HTTP %d: %s" % (method, path, err.code, detail)
            )
        except urllib.error.URLError as err:
            last_problem = "could not reach the API (%s)" % (err.reason,)
            time.sleep(2 ** attempt)
            continue

        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            raise FetchError("%s %s did not return JSON" % (method, path))

    raise FetchError("%s %s kept failing: %s" % (method, path, last_problem))


# ----------------------------------------------------------------------------
# The individual endpoints
# ----------------------------------------------------------------------------


def check_token(token):
    """Confirm the token works before doing anything else."""
    try:
        api_call("GET", "/me", token)
    except FetchError as err:
        raise FetchError(
            "the token was rejected, so nothing else was tried: %s" % (err,)
        )


def fetch_total(token, start, end):
    """GET /stats/total. Gives the visitor total and a day by day series."""
    return api_call("GET", "/stats/total", token, {"start": start, "end": end})


def fetch_hits(token, start, end):
    """
    GET /stats/hits. Every path with its visitor count for the window.

    The endpoint returns at most 100 paths per call, so when it says there is
    more we ask again and exclude the paths we already have.
    """
    rows = []
    seen_ids = []
    while True:
        params = {"start": start, "end": end, "limit": 100}
        if seen_ids:
            params["exclude_paths"] = ",".join(seen_ids)
        payload = api_call("GET", "/stats/hits", token, params)
        page = payload.get("hits") or []
        rows.extend(page)
        if not page or not payload.get("more"):
            break
        seen_ids.extend(str(row.get("path_id")) for row in page)
        if len(seen_ids) > 1000:
            raise FetchError("stats/hits still reported more paths after 1000")
    return rows


def fetch_breakdown(token, page, start, end, limit):
    """GET /stats/{page} for browsers, systems, locations, sizes, toprefs."""
    payload = api_call(
        "GET", "/stats/" + page, token, {"start": start, "end": end, "limit": limit}
    )
    return payload.get("stats") or []


# ----------------------------------------------------------------------------
# The CSV export, which is the only source of real pageview counts
# ----------------------------------------------------------------------------


def fetch_pageviews(token):
    """
    Count individual pageviews from a CSV export.

    Returns a dict with a count per day and a count per day per path, or None
    when the export is not available. Not available is the normal answer unless
    "Individual pageviews" is switched on in the GoatCounter site settings, so
    this never fails the run.
    """
    if os.environ.get("GOATCOUNTER_SKIP_EXPORT"):
        print("Skipping the CSV export because GOATCOUNTER_SKIP_EXPORT is set.")
        return None

    try:
        started = api_call("POST", "/export", token, body={"format": "csv"})
    except FetchError as err:
        print("No pageview counts: could not start the export (%s)." % (err,))
        return None

    export_id = started.get("id")
    if not export_id:
        print("No pageview counts: the export did not come back with an id.")
        return None

    # The export is built in the background, so wait for it to finish.
    waited = 0
    while True:
        try:
            status = api_call("GET", "/export/%d" % (export_id,), token)
        except FetchError as err:
            print("No pageview counts: could not check on the export (%s)." % (err,))
            return None
        if status.get("error"):
            print("No pageview counts: the export failed (%s)." % (status["error"],))
            return None
        if status.get("finished_at"):
            break
        if waited >= EXPORT_MAX_WAIT_SECONDS:
            print(
                "No pageview counts: the export was still running after %d seconds."
                % (EXPORT_MAX_WAIT_SECONDS,)
            )
            return None
        time.sleep(EXPORT_POLL_SECONDS)
        waited += EXPORT_POLL_SECONDS

    try:
        return _read_export(token, export_id)
    except FetchError as err:
        print("No pageview counts: %s." % (err,))
        return None


def _read_export(token, export_id):
    """Download the gzipped CSV and add up the rows."""
    url = "%s/export/%d/download" % (API_BASE, export_id)
    _throttle()
    try:
        response = urllib.request.urlopen(
            _build_request("GET", url, token), timeout=REQUEST_TIMEOUT
        )
    except urllib.error.HTTPError as err:
        raise FetchError("the download failed with HTTP %d" % (err.code,))
    except urllib.error.URLError as err:
        raise FetchError("the download could not be reached (%s)" % (err.reason,))

    by_day = {}
    by_path_day = {}
    with response:
        stream = io.TextIOWrapper(
            gzip.GzipFile(fileobj=response), encoding="utf-8", newline=""
        )
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            raise FetchError("the export was empty")

        # The first cell of the header carries the format version, as in
        # "2,Path". GoatCounter asks scripts to stop if that version changes,
        # because the columns may have moved.
        version = header[0].split(",", 1)[0].strip()
        if version != "2":
            raise FetchError(
                "the export format is version %r and this script reads version 2"
                % (version,)
            )

        path_col, bot_col, date_col = 0, 7, 13
        for row in reader:
            if len(row) <= date_col:
                continue
            # Bot is 0 for a real visitor and one of the isbot codes otherwise.
            # GoatCounter leaves bots out of its own totals, so we do too.
            bot = row[bot_col].strip()
            if bot not in ("", "0"):
                continue
            day = row[date_col][:10]
            if len(day) != 10:
                continue
            path = normalise_path(row[path_col])
            by_day[day] = by_day.get(day, 0) + 1
            by_path_day.setdefault(path, {})
            by_path_day[path][day] = by_path_day[path].get(day, 0) + 1

    return {"by_day": by_day, "by_path_day": by_path_day}


# ----------------------------------------------------------------------------
# Turning paths into pages and projects
# ----------------------------------------------------------------------------


def normalise_path(raw):
    """
    Tidy a recorded path into the form the dashboard shows.

    Drops any query string, drops the /artificialminds prefix, and folds
    index.html into its folder, so /artificialminds/stillpoint/index.html and
    /artificialminds/stillpoint/ both become /stillpoint/.
    """
    path = (raw or "").split("?", 1)[0].split("#", 1)[0].strip()
    if not path.startswith("/"):
        path = "/" + path
    lowered = path.lower()
    prefix = SITE_PREFIX.lower()
    if lowered == prefix:
        path = "/"
    elif lowered.startswith(prefix + "/"):
        path = path[len(SITE_PREFIX):]
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return path or "/"


def project_for(path):
    """
    Which project a page belongs to, or None for anything that is neither a
    project page nor the home page. The path must already be normalised.
    """
    if path == "/":
        return HOME_ID
    first_segment = path.strip("/").split("/", 1)[0].lower()
    for project_id, _ in PROJECTS:
        if project_id.lower() == first_segment:
            return project_id
    return None


def as_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


# ----------------------------------------------------------------------------
# Building the file
# ----------------------------------------------------------------------------


def utc_stamp(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def day_series(total_payload):
    """Turn the day by day part of /stats/total into {"YYYY-MM-DD": visitors}."""
    series = {}
    for row in total_payload.get("stats") or []:
        day = row.get("day")
        if not day:
            continue
        series[day] = series.get(day, 0) + as_int(row.get("daily"))
    return series


def visitors_by_path(hit_rows):
    """Sum the visitor counts per normalised path."""
    totals = {}
    for row in hit_rows:
        path = normalise_path(row.get("path"))
        totals[path] = totals.get(path, 0) + as_int(row.get("count"))
    return totals


def views_by_path(pageviews, since=None):
    """Sum pageviews per path, optionally only from a given day onwards."""
    if not pageviews:
        return {}
    totals = {}
    for path, days in pageviews["by_path_day"].items():
        count = 0
        for day, hits in days.items():
            if since is None or day >= since:
                count += hits
        if count:
            totals[path] = count
    return totals


def views_in_window(pageviews, since=None):
    if not pageviews:
        return 0
    return sum(
        hits
        for day, hits in pageviews["by_day"].items()
        if since is None or day >= since
    )


def load_previous(path):
    """Read the file from the last run. A missing or broken file is not fatal."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            previous = json.load(handle)
    except (OSError, ValueError) as err:
        print("Could not read the previous %s (%s), starting fresh." % (path, err))
        return {}
    return previous if isinstance(previous, dict) else {}


def previous_months(previous):
    months = {}
    for row in previous.get("monthly") or []:
        month = row.get("month")
        if month:
            months[month] = {
                "views": as_int(row.get("views")),
                "visitors": as_int(row.get("visitors")),
            }
    return months


def previous_by_key(previous, section, key):
    lookup = {}
    for row in previous.get(section) or []:
        if row.get(key):
            lookup[row[key]] = row
    return lookup


def build(token):
    """Make every call, then assemble the file. Nothing is written here."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    today = now.date()
    end = utc_stamp(now)
    start_30 = utc_stamp(
        datetime.combine(
            today - timedelta(days=SUMMARY_DAYS - 1), datetime.min.time(), timezone.utc
        )
    )
    first_day_30 = (today - timedelta(days=SUMMARY_DAYS - 1)).isoformat()
    first_day_90 = today - timedelta(days=DAILY_DAYS - 1)

    check_token(token)

    # One call covers the all-time visitor total and the whole day by day
    # history, which is where the 90 day series and the monthly series come from.
    total_all = fetch_total(token, ALL_TIME_START, end)
    total_30 = fetch_total(token, start_30, end)
    hits_all = fetch_hits(token, ALL_TIME_START, end)
    hits_30 = fetch_hits(token, start_30, end)
    countries = fetch_breakdown(token, "locations", start_30, end, 20)
    browsers = fetch_breakdown(token, "browsers", start_30, end, 20)
    systems = fetch_breakdown(token, "systems", start_30, end, 20)
    sizes = fetch_breakdown(token, "sizes", start_30, end, 10)
    referrers = fetch_breakdown(token, "toprefs", start_30, end, 15)

    # Pageviews are a nice to have. If the export is off, views fall back to
    # visitors further down.
    pageviews = fetch_pageviews(token)

    previous = load_previous(OUTPUT_PATH)

    visitors_per_day = day_series(total_all)
    views_per_day = pageviews["by_day"] if pageviews else {}

    # The day by day series, with a row for every day so the chart has no gaps.
    daily = []
    for offset in range(DAILY_DAYS):
        day = (first_day_90 + timedelta(days=offset)).isoformat()
        visitors = visitors_per_day.get(day, 0)
        daily.append(
            {
                "day": day,
                "views": max(views_per_day.get(day, 0), visitors),
                "visitors": visitors,
            }
        )

    # Months. Only months that actually have visitors are recomputed, and
    # everything else the previous file knew about is carried forward, so
    # history survives even after GoatCounter's own data ages out.
    fresh_months = {}
    for day, visitors in visitors_per_day.items():
        if visitors <= 0:
            continue
        month = day[:7]
        bucket = fresh_months.setdefault(month, {"views": 0, "visitors": 0})
        bucket["visitors"] += visitors
        bucket["views"] += views_per_day.get(day, 0)
    for month, bucket in fresh_months.items():
        bucket["views"] = max(bucket["views"], bucket["visitors"])

    merged_months = previous_months(previous)
    merged_months.update(fresh_months)
    monthly = [
        {
            "month": month,
            "views": merged_months[month]["views"],
            "visitors": merged_months[month]["visitors"],
        }
        for month in sorted(merged_months)
    ]

    # Pages and projects.
    visitors_all_by_path = visitors_by_path(hits_all)
    visitors_30_by_path = visitors_by_path(hits_30)
    views_all_by_path = views_by_path(pageviews)
    views_30_by_path = views_by_path(pageviews, since=first_day_30)

    old_pages = previous_by_key(previous, "pages", "path")
    pages = []
    for path, visitors in visitors_all_by_path.items():
        views = max(views_all_by_path.get(path, 0), visitors)
        old = old_pages.get(path, {})
        pages.append(
            {
                "path": path,
                # All-time counters never go down.
                "views_all": max(views, as_int(old.get("views_all"))),
                "visitors_all": max(visitors, as_int(old.get("visitors_all"))),
            }
        )
    pages.sort(key=lambda row: (-row["views_all"], row["path"]))
    pages = pages[:20]

    old_projects = previous_by_key(previous, "projects", "id")
    projects = []
    for project_id, name in PROJECTS + [(HOME_ID, HOME_NAME)]:
        visitors_all = sum(
            count
            for path, count in visitors_all_by_path.items()
            if project_for(path) == project_id
        )
        visitors_30 = sum(
            count
            for path, count in visitors_30_by_path.items()
            if project_for(path) == project_id
        )
        views_all = max(
            sum(
                count
                for path, count in views_all_by_path.items()
                if project_for(path) == project_id
            ),
            visitors_all,
        )
        views_30 = max(
            sum(
                count
                for path, count in views_30_by_path.items()
                if project_for(path) == project_id
            ),
            visitors_30,
        )
        old = old_projects.get(project_id, {})
        projects.append(
            {
                "id": project_id,
                "name": name,
                # All-time counters never go down. The 30 day ones are meant to
                # move in both directions, so they are always taken fresh.
                "views_all": max(views_all, as_int(old.get("views_all"))),
                "visitors_all": max(visitors_all, as_int(old.get("visitors_all"))),
                "views_30d": views_30,
                "visitors_30d": visitors_30,
            }
        )

    old_totals = previous.get("totals") or {}
    visitors_all = as_int(total_all.get("total"))
    visitors_30 = as_int(total_30.get("total"))
    totals = {
        "views_all": max(
            views_in_window(pageviews),
            visitors_all,
            as_int(old_totals.get("views_all")),
        ),
        "visitors_all": max(visitors_all, as_int(old_totals.get("visitors_all"))),
        "views_30d": max(views_in_window(pageviews, since=first_day_30), visitors_30),
        "visitors_30d": visitors_30,
    }

    return {
        "generated": utc_stamp(now),
        "totals": totals,
        "daily": daily,
        "monthly": monthly,
        "projects": projects,
        "pages": pages,
        "countries": named_counts(countries, 20),
        "browsers": named_counts(browsers, 20),
        "systems": named_counts(systems, 20),
        "sizes": named_counts(sizes, 10, names=SIZE_NAMES),
        "referrers": named_counts(referrers, 15),
    }


def named_counts(stats, limit, names=None):
    """
    Turn a breakdown into [{"name": ..., "visitors": ...}].

    Some breakdowns, screen sizes above all, come back with an id and an empty
    name, so the id is looked up in a table of readable labels.
    """
    rows = []
    for stat in stats:
        label = (stat.get("name") or "").strip()
        key = (stat.get("id") or "").strip()
        if names:
            label = names.get(key.lower(), label or key)
        if not label:
            label = key or "Unknown"
        rows.append({"name": label, "visitors": as_int(stat.get("count"))})
    rows.sort(key=lambda row: (-row["visitors"], row["name"]))
    return rows[:limit]


def write_atomically(path, data):
    """Write to a temporary file first so a crash cannot leave a broken file."""
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(temporary, path)


def main():
    token = os.environ.get("GOATCOUNTER_TOKEN", "").strip()
    if not token:
        print(
            "GOATCOUNTER_TOKEN is not set. Put the GoatCounter API token in that\n"
            "environment variable and run this again. In the GitHub Action it comes\n"
            "from the GOATCOUNTER_TOKEN repository secret. Nothing was written.",
            file=sys.stderr,
        )
        return 1

    try:
        data = build(token)
    except FetchError as err:
        print(
            "Could not fetch the stats: %s\n"
            "%s was left exactly as it was." % (err, OUTPUT_PATH),
            file=sys.stderr,
        )
        return 1

    write_atomically(OUTPUT_PATH, data)
    print(
        "Wrote %s: %d visitors all time, %d in the last %d days, %d pages, %d months."
        % (
            OUTPUT_PATH,
            data["totals"]["visitors_all"],
            data["totals"]["visitors_30d"],
            SUMMARY_DAYS,
            len(data["pages"]),
            len(data["monthly"]),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
