# Where the numbers on the stats page come from

`fetch_stats.py` reads the site's traffic from the GoatCounter API and writes
`stats/data.json`, which the dashboard page loads. Standard library only. Run it
by hand with:

    GOATCOUNTER_TOKEN=... python3 scripts/fetch_stats.py

`.github/workflows/stats.yml` runs it every six hours, and on demand from the
Actions tab. It commits `stats/data.json` only when the numbers have moved. That
file must sit at the repository root under `.github/workflows/` or GitHub will
not run it.

Two notes. The statistics API counts visits, not pageviews, so the script also
downloads a CSV export for real pageview counts. That export needs "Individual
pageviews" switched on in the GoatCounter settings; without it the views figures
fall back to the visitor figures. And all-time counters never go down: the
script keeps the previous file's monthly history and takes the larger of the old
and the new value, so nothing is lost when GoatCounter's data ages out.
