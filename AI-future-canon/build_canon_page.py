#!/usr/bin/env python3
import json, base64, html, sys, re

DATA = sys.argv[1] if len(sys.argv) > 1 else 'canon-data.json'
COVERS = sys.argv[2] if len(sys.argv) > 2 else 'covers'
OUT = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/ai-future-canon.html'

d = json.load(open(DATA))
fiction, nonfiction, rest = d['fiction'], d['nonfiction'], d['rest']
notes = {e['elder']: e for e in d['elder_notes']}
ELDER_NAMES = {'historian': 'The Historian', 'practitioner': 'The Builder', 'sage': 'The Sage'}
ELDER_ORDER = ['historian', 'practitioner', 'sage']

def scrub(s):
    if not s: return s
    s = re.sub(r'\s*—\s*', ', ', s)
    s = re.sub(r',\s*,', ',', s)
    s = re.sub(r':\s*,\s*', ': ', s)
    s = re.sub(r'\(\s*,\s*', '(', s).replace(' ,', ',')
    return s

for lst in (fiction, nonfiction, rest):
    for b in lst:
        b['synopsis'] = scrub(b.get('synopsis',''))
        b['why_it_matters'] = scrub(b.get('why_it_matters',''))
        b['key_predictions'] = [scrub(p) for p in b.get('key_predictions',[])]
        b['elder_verdicts'] = [scrub(v) for v in b.get('elder_verdicts',[])]
for e in notes.values():
    e['note'] = scrub(e['note'])

def esc(s): return html.escape(s or '', quote=True)

def cover(lst, j):
    with open(f'{COVERS}/{lst}_{j:02d}.jpg', 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()

all_books = fiction + nonfiction + rest
years = [b['year'] for b in all_books]
n_fic = sum(1 for b in all_books if b['kind'] == 'fiction')
n_non = len(all_books) - n_fic

def meters(b, compact=False):
    pp, prep = b['predictive_power'], b['preparation_value']
    cls = ' compact' if compact else ''
    l1, l2 = ('Predictive', 'Prepares') if compact else ('Predictive power', 'Preparation')
    return f'''<div class="meters{cls}">
  <div class="meter"><span class="meter-label">{l1}</span>
    <span class="meter-track"><span class="meter-fill pp" style="width:{pp}%"></span></span>
    <span class="meter-val">{pp}<small>%</small></span></div>
  <div class="meter"><span class="meter-label">{l2}</span>
    <span class="meter-track"><span class="meter-fill prep" style="width:{prep}%"></span></span>
    <span class="meter-val">{prep}<small>%</small></span></div>
</div>'''

# ---------- JS data (no covers; covers read from card img at open time) ----------
js_books = {}
def reg(b, bid, shelf_label, rank_label):
    js_books[bid] = {
        'shelf': shelf_label, 'rank': rank_label,
        'title': b['title'], 'author': b['author'], 'year': b['year'], 'kind': b['kind'],
        'pp': b['predictive_power'], 'prep': b['preparation_value'],
        'synopsis': b.get('synopsis',''), 'wim': b.get('why_it_matters',''),
        'preds': b.get('key_predictions', []),
        'reviews': [{'q': r['quote'], 's': r['source']} for r in (b.get('reviews') or [])[:4]],
        'verdicts': b.get('elder_verdicts', [])[:3],
    }

def shelf_card(b, lst, j, rank):
    bid = f'{lst[0]}{j}'
    reg(b, bid, 'Fiction top 10' if lst == 'fiction' else 'Nonfiction top 10', f'#{rank}')
    return f'''<article class="card shelf-card" data-id="{bid}" role="button" tabindex="0" aria-haspopup="dialog" aria-label="Open details for {esc(b['title'])}">
  <div class="shelf-head">
    <div class="shelf-rank">{rank}</div>
    <div class="shelf-cover"><img src="{cover(lst, j)}" alt="Cover of {esc(b['title'])}" loading="lazy"></div>
    <div class="shelf-title-wrap">
      <div class="meta-line"><span class="year">{b['year']}</span></div>
      <h3 class="book-title">{esc(b['title'])}</h3>
      <p class="book-author">{esc(b['author'])}</p>
      {meters(b)}
    </div>
  </div>
  <p class="synopsis">{esc(b['synopsis'])}</p>
  <span class="open-hint">Click for the full story &#8599;</span>
</article>'''

fic_cards = ''.join(shelf_card(b, 'fiction', j, j + 1) for j, b in enumerate(fiction))
non_cards = ''.join(shelf_card(b, 'nonfiction', j, j + 1) for j, b in enumerate(nonfiction))

grid_cards = []
for j, b in enumerate(rest):
    rank = j + 21
    bid = f'r{j}'
    reg(b, bid, 'The next 50', f'#{rank}')
    grid_cards.append(f'''<article class="card mini-card" data-id="{bid}" data-kind="{b['kind']}" role="button" tabindex="0" aria-haspopup="dialog" aria-label="Open details for {esc(b['title'])}">
  <div class="mini-top">
    <span class="rank-num">{rank}</span>
    <span class="kind-chip">{b['kind']}</span>
    <span class="year">{b['year']}</span>
  </div>
  <div class="mini-cover"><img src="{cover('rest', j)}" alt="Cover of {esc(b['title'])}" loading="lazy"></div>
  <h3 class="book-title">{esc(b['title'])}</h3>
  <p class="book-author">{esc(b['author'])}</p>
  {meters(b, compact=True)}
  <p class="synopsis clamp">{esc(b['synopsis'])}</p>
  <span class="open-hint">Click for the full story &#8599;</span>
</article>''')

counsel = ''.join(f'''<div class="counsel"><h4>{esc(ELDER_NAMES[k])}</h4><p>{esc(notes[k]['note'])}</p></div>''' for k in ELDER_ORDER)

def trow(shelf, rank, b):
    return (f'<tr><td>{shelf}</td><td>{rank}</td><td>{esc(b["title"])}</td><td>{esc(b["author"])}</td>'
            f'<td>{b["year"]}</td><td>{b["kind"]}</td><td>{b["predictive_power"]}%</td><td>{b["preparation_value"]}%</td></tr>')
rows = ''.join(trow('Fiction top 10', j+1, b) for j, b in enumerate(fiction))
rows += ''.join(trow('Nonfiction top 10', j+1, b) for j, b in enumerate(nonfiction))
rows += ''.join(trow('The next 50', j+21, b) for j, b in enumerate(rest))

BOOK_ICON = '''<svg class="book-icon" viewBox="0 0 48 40" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
<path d="M24 8 C20 4.5 14 3.5 8 3.5 C6 3.5 4.5 3.7 3 4 L3 32 C4.5 31.7 6 31.5 8 31.5 C14 31.5 20 32.5 24 36 C28 32.5 34 31.5 40 31.5 C42 31.5 43.5 31.7 45 32 L45 4 C43.5 3.7 42 3.5 40 3.5 C34 3.5 28 4.5 24 8 Z"/>
<path d="M24 8 L24 36"/>
</svg>'''

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The AI-Future Canon: 70 books to get you ready for the world that is coming</title>
<meta name="description" content="Seventy books, scored on how much of the AI future they saw coming and how well they prepare you for it.">
<style>
:root {{
  color-scheme: light;
  --plane: #edece7; --surface: #fcfcfb;
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --hairline: #dcdbd4; --border: rgba(11,11,11,0.10);
  --track: #e7e6df; --shadow: 0 12px 32px rgba(11,11,11,0.16), 0 3px 8px rgba(11,11,11,0.09);
  --pp: #2a78d6; --prep: #eb6834;
  --serif: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
  --sans: system-ui, -apple-system, 'Segoe UI', sans-serif;
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --plane: #0d0d0d; --surface: #1a1a19;
  --ink: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
  --hairline: #2c2c2a; --border: rgba(255,255,255,0.10);
  --track: #262624; --shadow: 0 12px 32px rgba(0,0,0,0.55), 0 3px 8px rgba(0,0,0,0.4);
  --pp: #3987e5; --prep: #d95926;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--plane); color: var(--ink); font-family: var(--sans); line-height: 1.55; -webkit-font-smoothing: antialiased; }}
.wrap {{ max-width: 1240px; margin: 0 auto; padding: 56px 28px 80px; }}

header.page-head {{ text-align: center; margin-bottom: 40px; }}
.book-icon {{ width: 44px; height: 37px; color: var(--muted); margin-bottom: 10px; }}
.overline {{ font-size: 12px; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); margin-bottom: 14px; }}
h1 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(34px, 5vw, 52px); letter-spacing: -0.01em; }}
.sub {{ max-width: 640px; margin: 14px auto 0; color: var(--ink-2); font-size: 16px; }}
.howto {{ max-width: 700px; margin: 22px auto 0; padding: 16px 22px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; text-align: left; }}
.howto p {{ font-size: 14px; color: var(--ink-2); }}
.howto p + p {{ margin-top: 8px; }}
.howto strong {{ color: var(--ink); font-weight: 600; }}
.statline {{ display: flex; justify-content: center; gap: 28px; flex-wrap: wrap; margin-top: 28px; padding: 16px 0; border-top: 1px solid var(--hairline); border-bottom: 1px solid var(--hairline); }}
.stat {{ text-align: center; }}
.stat b {{ display: block; font-size: 22px; font-weight: 600; }}
.stat span {{ font-size: 11.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}

.chip {{ font: 13px var(--sans); padding: 6px 14px; border-radius: 999px; border: 1px solid var(--hairline); background: transparent; color: var(--ink-2); cursor: pointer; }}
.chip[aria-pressed="true"] {{ background: var(--ink); color: var(--plane); border-color: var(--ink); }}
.theme-toggle {{ position: fixed; top: 16px; right: 16px; z-index: 40; display: flex; align-items: center; gap: 7px;
  font: 600 13px var(--sans); padding: 9px 16px; border-radius: 999px; cursor: pointer;
  background: var(--surface); color: var(--ink); border: 1px solid var(--hairline);
  box-shadow: 0 4px 14px rgba(11,11,11,0.12); }}
.theme-toggle:hover {{ box-shadow: 0 6px 18px rgba(11,11,11,0.2); }}
.theme-toggle svg {{ width: 15px; height: 15px; }}

.section-head {{ margin: 56px 0 8px; text-align: center; }}
.section-head h2 {{ font-family: var(--serif); font-weight: 500; font-size: 27px; }}
.section-head p {{ color: var(--ink-2); font-size: 14.5px; max-width: 600px; margin: 8px auto 0; }}

.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }}
[role="button"].card {{ cursor: pointer; position: relative; transition: box-shadow .18s ease, transform .18s ease, border-color .18s ease; }}
[role="button"].card:hover, [role="button"].card:focus-visible {{ box-shadow: var(--shadow); transform: translateY(-3px); border-color: var(--muted); }}
[role="button"].card:focus-visible {{ outline: 2px solid var(--pp); outline-offset: 2px; }}
.open-hint {{ display: block; margin-top: 10px; font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: var(--pp); opacity: 0; transition: opacity .18s ease; }}
[role="button"].card:hover .open-hint, [role="button"].card:focus-visible .open-hint {{ opacity: 1; }}

.meta-line {{ display: flex; align-items: center; gap: 10px; }}
.kind-chip {{ font-size: 10px; letter-spacing: .1em; text-transform: uppercase; padding: 1px 7px; border-radius: 999px; border: 1px solid var(--hairline); color: var(--ink-2); }}
.year {{ font-size: 12.5px; color: var(--muted); }}
.rank-num {{ font-family: var(--serif); font-size: 16px; color: var(--muted); }}
.book-title {{ font-family: var(--serif); font-weight: 500; font-size: 18px; line-height: 1.25; }}
.book-author {{ color: var(--ink-2); font-size: 13.5px; margin-top: 2px; }}

.meters {{ margin-top: 10px; display: flex; flex-direction: column; gap: 6px; max-width: 420px; }}
.meter {{ display: grid; grid-template-columns: 106px 1fr 42px; align-items: center; gap: 9px; }}
.meters.compact .meter {{ grid-template-columns: 62px 1fr 36px; gap: 7px; }}
.meter-label {{ font-size: 10.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }}
.meters.compact .meter-label {{ font-size: 9.5px; }}
.meter-track {{ height: 6px; background: var(--track); border-radius: 4px; overflow: hidden; display: block; }}
.meter-fill {{ display: block; height: 100%; border-radius: 4px; }}
.meter-fill.pp {{ background: var(--pp); }}
.meter-fill.prep {{ background: var(--prep); }}
.meter-val {{ font-size: 13px; font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }}
.meter-val small {{ font-size: 9px; color: var(--muted); font-weight: 400; }}

.synopsis {{ margin-top: 11px; font-size: 13.5px; color: var(--ink-2); }}
.clamp {{ display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }}

/* top shelf */
.shelves {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 8px; align-items: start; }}
.shelf-sticky {{ position: sticky; top: 0; z-index: 20; background: var(--plane); text-align: center; padding: 12px 0 9px; border-bottom: 1px solid var(--hairline); }}
.shelf-sticky h3 {{ font-family: var(--serif); font-weight: 500; font-size: 20px; }}
.shelf-sticky p {{ font-size: 12.5px; color: var(--muted); margin-top: 1px; }}
.shelf-card {{ padding: 18px 20px; margin-top: 14px; }}
.shelf-head {{ display: grid; grid-template-columns: 34px 74px 1fr; gap: 14px; align-items: start; }}
.shelf-rank {{ font-family: var(--serif); font-size: 26px; color: var(--muted); line-height: 1.1; padding-top: 2px; }}
.shelf-cover img {{ width: 100%; border-radius: 4px; border: 1px solid var(--border); display: block; }}

/* next-50 grid */
.controls {{ display: flex; justify-content: center; gap: 8px; margin: 20px 0 0; flex-wrap: wrap; }}
.grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-top: 18px; }}
.mini-card {{ padding: 14px; display: flex; flex-direction: column; }}
.mini-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 9px; }}
.mini-cover {{ display: flex; justify-content: center; margin-bottom: 10px; }}
.mini-cover img {{ height: 132px; width: auto; max-width: 100%; border-radius: 3px; border: 1px solid var(--border); }}
.mini-card .book-title {{ font-size: 15px; }}
.mini-card .book-author {{ font-size: 12.5px; }}
.mini-card .synopsis {{ font-size: 12.5px; }}
.mini-card .open-hint {{ margin-top: auto; padding-top: 10px; }}

.counsel-wrap {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 18px; }}
.counsel {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }}
.counsel h4 {{ font-size: 11.5px; letter-spacing: .12em; text-transform: uppercase; color: var(--pp); margin-bottom: 8px; }}
.counsel p {{ font-size: 13px; color: var(--ink-2); }}

.tablewrap {{ margin-top: 48px; }}
.tablewrap summary {{ cursor: pointer; font-size: 12.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); text-align: center; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }}
th, td {{ text-align: left; padding: 7px 11px; border-bottom: 1px solid var(--hairline); }}
th {{ font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
td:nth-child(2), td:nth-child(7), td:nth-child(8) {{ font-variant-numeric: tabular-nums; }}

footer {{ margin-top: 56px; text-align: center; color: var(--muted); font-size: 12.5px; }}
footer p {{ max-width: 640px; margin: 4px auto; }}
.card[hidden] {{ display: none; }}

/* modal */
.modal-backdrop {{ position: fixed; inset: 0; background: rgba(11,11,11,0.5); backdrop-filter: blur(3px); z-index: 90; display: none; }}
.modal-backdrop.open {{ display: block; }}
.modal {{ position: fixed; inset: 0; z-index: 100; display: none; align-items: center; justify-content: center; padding: 24px; }}
.modal.open {{ display: flex; }}
.modal-dialog {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; box-shadow: var(--shadow);
  max-width: 880px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 30px 32px; position: relative; }}
.modal-close {{ position: absolute; top: 14px; right: 14px; width: 34px; height: 34px; border-radius: 999px;
  border: 1px solid var(--hairline); background: var(--surface); color: var(--ink-2); font-size: 17px; cursor: pointer; line-height: 1; }}
.modal-close:hover {{ color: var(--ink); border-color: var(--muted); }}
.modal-grid {{ display: grid; grid-template-columns: 240px 1fr; gap: 28px; align-items: start; }}
.modal-cover img {{ width: 100%; border-radius: 6px; border: 1px solid var(--border); display: block; box-shadow: 0 8px 24px rgba(11,11,11,0.18); }}
.modal-cover .meters {{ margin-top: 16px; max-width: none; }}
.modal-shelf {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--pp); font-weight: 600; }}
.modal-title {{ font-family: var(--serif); font-weight: 500; font-size: 26px; line-height: 1.2; margin-top: 6px; }}
.modal-byline {{ color: var(--ink-2); font-size: 14.5px; margin-top: 4px; }}
.modal-section {{ margin-top: 18px; }}
.modal-section h5 {{ font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }}
.modal-section p {{ font-size: 14.5px; color: var(--ink-2); }}
.modal-section ul {{ margin-left: 18px; font-size: 14px; color: var(--ink-2); }}
.modal-section ul li {{ margin-bottom: 5px; }}
.modal-reviews {{ display: grid; gap: 12px; }}
.modal .review p {{ font-size: 14px; }}
.modal-verdicts {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
.modal .verdict-elder {{ font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: var(--pp); font-weight: 600; }}
.modal .verdict p {{ font-size: 13px; color: var(--ink-2); margin-top: 3px; }}
.review {{ border-left: 2px solid var(--hairline); padding-left: 12px; }}
.review p {{ font-family: var(--serif); font-style: italic; color: var(--ink); }}
.review cite {{ display: block; margin-top: 4px; font-style: normal; font-size: 12px; color: var(--muted); }}

@media (max-width: 1100px) {{ .grid {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (max-width: 900px) {{ .shelves {{ grid-template-columns: 1fr; }} }}
@media (max-width: 680px) {{
  .grid {{ grid-template-columns: repeat(2, 1fr); }}
  .counsel-wrap {{ grid-template-columns: 1fr; }}
  .modal-grid {{ grid-template-columns: 1fr; }}
  .modal-cover {{ max-width: 220px; margin: 0 auto; }}
  .modal-verdicts {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 460px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<button class="theme-toggle" id="themeBtn" aria-label="Switch between light and dark mode">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12h2.5M19 12h2.5M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8"/></svg>
  <span id="themeLabel">Dark mode</span>
</button>
<div class="wrap">
<header class="page-head">
  {BOOK_ICON}
  <div class="overline">A reading list for the age of AI</div>
  <h1>The AI-Future Canon</h1>
  <p class="sub">In a few years, people and AI will live and work side by side everywhere. These 70 books, some stories and some serious forecasts, saw parts of that world before it arrived. Read even a few and you will be far better prepared than most.</p>
  <div class="howto">
    <p><strong>How the books were chosen.</strong> Every book was put before a council of three elders: a historian who checks each prediction against what really happened, a builder who works on AI systems today, and a sage who studies how people and societies handle big change. Chosen from {d['total_candidates']} books considered.</p>
    <p><strong>How to read the scores.</strong> <strong>Predictive power</strong> means how much of what the book guessed has actually come true so far. <strong>Preparation</strong> means how much wiser the book leaves you about the world that is coming. Both are averages of the three elders' scores.</p>
  </div>
  <div class="statline">
    <div class="stat"><b>70</b><span>books</span></div>
    <div class="stat"><b>{d['total_candidates']}</b><span>considered</span></div>
    <div class="stat"><b>{min(years)}&ndash;{max(years)}</b><span>years covered</span></div>
    <div class="stat"><b>{n_fic}&thinsp;/&thinsp;{n_non}</b><span>fiction / nonfiction</span></div>
  </div>
</header>

<section>
  <div class="section-head">
    <h2>The Top Shelf</h2>
    <p>The ten best stories and the ten best nonfiction books, each ranked on their own shelf. Stories prepare the heart; nonfiction prepares the head. You need both. Click any book for its full story.</p>
  </div>
  <div class="shelves">
    <div class="shelf-col" id="ficCol">
      <div class="shelf-sticky"><h3>Fiction</h3><p>The ten best stories, ranked</p></div>
      {fic_cards}
    </div>
    <div class="shelf-col" id="nonCol">
      <div class="shelf-sticky"><h3>Nonfiction</h3><p>The ten best true books, ranked</p></div>
      {non_cards}
    </div>
  </div>
</section>

<section>
  <div class="section-head">
    <h2>The Next 50</h2>
    <p>One single ranking from 21 to 70, fiction and nonfiction mixed together and judged by the same scores. Use the buttons to show just one kind.</p>
  </div>
  <div class="controls" role="group" aria-label="Filter by kind">
    <button class="chip" data-filter="all" aria-pressed="true">All 50</button>
    <button class="chip" data-filter="fiction" aria-pressed="false">Fiction</button>
    <button class="chip" data-filter="nonfiction" aria-pressed="false">Nonfiction</button>
  </div>
  <div class="grid">
    {''.join(grid_cards)}
  </div>
</section>

<section>
  <div class="section-head">
    <h2>Advice From the Elders</h2>
    <p>The three judges each left a short note for readers of this list.</p>
  </div>
  <div class="counsel-wrap">
    {counsel}
  </div>
</section>

<details class="tablewrap">
  <summary>See the full ranking as a table</summary>
  <table>
    <thead><tr><th>Shelf</th><th>#</th><th>Title</th><th>Author</th><th>Year</th><th>Kind</th><th>Predictive</th><th>Preparation</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</details>

<footer>
  <p>Review quotes are copied word for word from the named sources. Scores reflect what had actually happened in the world as of July 2026.</p>
</footer>
</div>

<div class="modal-backdrop" id="modalBackdrop"></div>
<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal-dialog">
    <button class="modal-close" id="modalClose" aria-label="Close">&#10005;</button>
    <div class="modal-grid">
      <div class="modal-cover">
        <img id="modalCover" src="" alt="">
        <div class="meters">
          <div class="meter"><span class="meter-label">Predictive power</span><span class="meter-track"><span class="meter-fill pp" id="mPP"></span></span><span class="meter-val" id="mPPv"></span></div>
          <div class="meter"><span class="meter-label">Preparation</span><span class="meter-track"><span class="meter-fill prep" id="mPrep"></span></span><span class="meter-val" id="mPrepv"></span></div>
        </div>
      </div>
      <div class="modal-body">
        <div class="modal-shelf" id="modalShelf"></div>
        <h4 class="modal-title" id="modalTitle"></h4>
        <p class="modal-byline" id="modalByline"></p>
        <div class="modal-section"><h5>What it is about</h5><p id="modalSynopsis"></p></div>
        <div class="modal-section" id="secWim"><h5>Why this book matters</h5><p id="modalWim"></p></div>
        <div class="modal-section" id="secPreds"><h5>What it predicted</h5><ul id="modalPreds"></ul></div>
        <div class="modal-section" id="secReviews"><h5>What reviewers said</h5><div class="modal-reviews" id="modalReviews"></div></div>
        <div class="modal-section" id="secVerdicts"><h5>The elders&rsquo; verdicts</h5><div class="modal-verdicts" id="modalVerdicts"></div></div>
      </div>
    </div>
  </div>
</div>

<script>
var BOOKS = {json.dumps(js_books, ensure_ascii=False)};
var ELDERS = ['The Historian', 'The Builder', 'The Sage'];
(function() {{
  var root = document.documentElement;
  var label = document.getElementById('themeLabel');
  document.getElementById('themeBtn').addEventListener('click', function() {{
    var dark = root.getAttribute('data-theme') === 'dark';
    root.setAttribute('data-theme', dark ? 'light' : 'dark');
    label.textContent = dark ? 'Dark mode' : 'Light mode';
  }});

  var chips = document.querySelectorAll('.chip[data-filter]');
  chips.forEach(function(c) {{
    c.addEventListener('click', function() {{
      chips.forEach(function(x) {{ x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); }});
      var f = c.getAttribute('data-filter');
      document.querySelectorAll('.grid .card[data-kind]').forEach(function(card) {{
        card.hidden = (f !== 'all' && card.getAttribute('data-kind') !== f);
      }});
    }});
  }});

  // equal-height rows for the two top-shelf columns
  function syncHeights() {{
    var fc = document.querySelectorAll('#ficCol .shelf-card');
    var nc = document.querySelectorAll('#nonCol .shelf-card');
    var two = window.matchMedia('(min-width: 901px)').matches;
    for (var i = 0; i < Math.max(fc.length, nc.length); i++) {{
      if (fc[i]) fc[i].style.minHeight = '';
      if (nc[i]) nc[i].style.minHeight = '';
    }}
    if (!two) return;
    for (var i = 0; i < Math.min(fc.length, nc.length); i++) {{
      var h = Math.max(fc[i].offsetHeight, nc[i].offsetHeight);
      fc[i].style.minHeight = h + 'px';
      nc[i].style.minHeight = h + 'px';
    }}
  }}
  window.addEventListener('load', syncHeights);
  window.addEventListener('resize', function() {{ clearTimeout(window.__sh); window.__sh = setTimeout(syncHeights, 120); }});

  // modal
  var modal = document.getElementById('modal'), backdrop = document.getElementById('modalBackdrop');
  var lastFocus = null;
  function openModal(id, card) {{
    var b = BOOKS[id];
    if (!b) return;
    lastFocus = card;
    var img = card.querySelector('img');
    var mc = document.getElementById('modalCover');
    mc.src = img ? img.src : '';
    mc.alt = 'Cover of ' + b.title;
    document.getElementById('modalShelf').textContent = b.shelf + ' \\u00b7 ' + b.rank + ' \\u00b7 ' + b.kind + ' \\u00b7 ' + b.year;
    document.getElementById('modalTitle').textContent = b.title;
    document.getElementById('modalByline').textContent = 'by ' + b.author;
    document.getElementById('modalSynopsis').textContent = b.synopsis;
    document.getElementById('mPP').style.width = b.pp + '%';
    document.getElementById('mPrep').style.width = b.prep + '%';
    document.getElementById('mPPv').textContent = b.pp + '%';
    document.getElementById('mPrepv').textContent = b.prep + '%';
    document.getElementById('secWim').style.display = b.wim ? '' : 'none';
    document.getElementById('modalWim').textContent = b.wim || '';
    var preds = document.getElementById('modalPreds'); preds.innerHTML = '';
    (b.preds || []).forEach(function(p) {{ var li = document.createElement('li'); li.textContent = p; preds.appendChild(li); }});
    document.getElementById('secPreds').style.display = (b.preds && b.preds.length) ? '' : 'none';
    var revs = document.getElementById('modalReviews'); revs.innerHTML = '';
    (b.reviews || []).forEach(function(r) {{
      var bq = document.createElement('blockquote'); bq.className = 'review';
      var p = document.createElement('p'); p.textContent = '\\u201c' + r.q + '\\u201d';
      var c = document.createElement('cite'); c.textContent = '\\u2013 ' + r.s;
      bq.appendChild(p); bq.appendChild(c); revs.appendChild(bq);
    }});
    document.getElementById('secReviews').style.display = (b.reviews && b.reviews.length) ? '' : 'none';
    var vs = document.getElementById('modalVerdicts'); vs.innerHTML = '';
    (b.verdicts || []).forEach(function(v, i) {{
      var dv = document.createElement('div'); dv.className = 'verdict';
      var s = document.createElement('span'); s.className = 'verdict-elder'; s.textContent = ELDERS[i] || 'Elder';
      var p = document.createElement('p'); p.textContent = v;
      dv.appendChild(s); dv.appendChild(p); vs.appendChild(dv);
    }});
    document.getElementById('secVerdicts').style.display = (b.verdicts && b.verdicts.length) ? '' : 'none';
    modal.classList.add('open'); backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
    document.getElementById('modalClose').focus();
  }}
  function closeModal() {{
    modal.classList.remove('open'); backdrop.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }}
  document.querySelectorAll('.card[data-id]').forEach(function(card) {{
    card.addEventListener('click', function() {{ openModal(card.getAttribute('data-id'), card); }});
    card.addEventListener('keydown', function(e) {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); openModal(card.getAttribute('data-id'), card); }}
    }});
  }});
  document.getElementById('modalClose').addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);
  modal.addEventListener('click', function(e) {{ if (e.target === modal) closeModal(); }});
  document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape' && modal.classList.contains('open')) closeModal(); }});
}})();
</script>
</body>
</html>'''

with open(OUT, 'w') as f:
    f.write(page)
print('written', len(page), 'bytes ->', OUT)
