# The AI-Future Canon: Methodology and Maintenance Guide

This document explains how the AI-Future Canon was built, the rules that govern it, and exactly how to update it. It is written for the agents (and humans) who will maintain the list as part of the owner's website. Read it fully before changing anything. The list is the product of five multi-agent deliberation rounds; ad-hoc edits that bypass the process described here will degrade its integrity.

## The files

- `ai-future-canon.html`: the published page. A single self-contained file: all CSS, all JavaScript, and all 70 cover images (base64 data URIs) are inline. It can be hosted anywhere or opened from disk.
- `canon-data.json`: the canonical dataset. The page is generated from this file. Edit the data here, never by hand-editing the HTML.
- `build_canon_page.py`: the page generator. Usage: `python3 build_canon_page.py canon-data.json covers/ ai-future-canon.html` where `covers/` holds one JPEG per book named `{fiction|nonfiction|rest}_{index:02d}.jpg` (zero-indexed within each section).
- `AI-Future-Canon-Methodology.md`: this file.

## Purpose and editorial north star

The canon exists so that a general reader, in a world a few years out where humans and AI coexist everywhere, can be an order of magnitude more prepared than most people. The stated mandate given to every judge is to EXPAND MINDS. That phrase is load-bearing: it is why checklist-style explainers score worse than books that change how a reader thinks, and it is the standard against which every candidate's case is argued.

Two kinds of books qualify: fiction (which prepares the heart: what it feels like to live with, love, raise, obey, and lose artificial minds) and serious predict-the-future nonfiction (which prepares the head: mechanisms, power, economics, failure modes). Recency gets some preference because books written close to the real technology tend to prepare readers better, but great older works are never discounted for age alone. The current list runs from 1909 (The Machine Stops) to 2025.

## The pipeline

The canon was built in rounds. Each round has three phases, and any future large revision should follow the same shape.

### Phase 1: Research agents

Parallel research agents (Opus-class), each with a distinct sourcing beat so their blind spots don't overlap. Beats used across the five rounds, reusable for future rounds: the modern AI era (2015 to present), the pre-2000 classics, near-future societal transformation, predictive nonfiction and futurism, international and translated wildcards, the nature of minds, the post-2023 LLM explainer wave, human-AI intimacy and daily life, big-canvas civilizational futures, published best-of lists and awards, books cited inside other canon books, blog and community reading lists (LessWrong, Astral Codex Ten, podcast recommendations), missing fiction, and adjacent fields (economics, war, biology, media theory, complex systems).

Every research agent must produce, per book: title, author, first-publication year, kind (fiction or nonfiction), ISBN-13 of a common edition, a 2-3 sentence synopsis, 2-4 key predictions, and a predictive_rationale written as the case that will be argued before the elders: concrete about what the book foresaw and what has verifiably panned out as of the scoring date.

**The verbatim review rule (non-negotiable).** Each book needs at least two review quotes copied word for word from real published reviews the agent actually fetched (Kirkus, Publishers Weekly, major outlets, serious blogs with named critics). Paraphrased or invented quotes are forbidden; publisher marketing blurbs don't count. If two real quotes cannot be verified, the book is dropped, whatever its merits. Quotes are never edited afterward, even to fix punctuation the site style would otherwise forbid.

### Phase 2: The Elder Council

Three judge agents (Opus-class, high reasoning effort) score every candidate in one sitting from a full docket. Their personas are fixed; reuse them verbatim so scores stay comparable across rounds:

- **The Elder Historian of Technology** (published as "The Historian"): scores prediction against the actual record, what a book claimed dated against what verifiably happened. Allergic to retroactive generosity: vague gestures at "thinking machines" earn little; specific, dated, falsifiable foresight earns much.
- **The Elder Practitioner** (published as "The Builder"): builds and deploys AI systems today. Scores books by how well their mechanisms match the technology that actually arrived: training on human data, emergent capability, misalignment-by-optimization, human-AI collaboration patterns, the texture of living with these systems.
- **The Elder Sage of Civilizations** (published as "The Sage"): cares about whether a book grasps how humans absorb transformative technology: institutions, self-deceptions, power grabs, quiet adaptations. Scores by the wisdom a reader carries out.

Each elder returns, for every candidate: `predictive_power` 0-100 (how much of what the book foresaw has actually happened by the scoring date; 85+ reserved for uncanny accuracy), `preparation_value` 0-100 (how much wiser it leaves a general reader about the coming decade), a one-sentence verdict, and an ordered top-five vote. Elders are instructed to spread scores across the full range and, since verdicts are published, to write them so a high school student gets them instantly.

### Phase 3: Plain Words

Every published field except review quotes is rewritten so a high school student can read it without slowing down: short sentences, everyday words, active voice, no jargon (or a five-word plain explanation when unavoidable). Facts, dates, names, and claims stay exactly accurate; only wording simplifies. Rewriter agents handle this in chunks; any new or revised entry must go through the same pass before publication.

## Scoring and selection math

- Published scores are the mean of the three elders, rounded: `predictive_power = round(mean(pp))`, `preparation_value = round(mean(prep))`.
- Ranking uses a composite: `composite = 0.5 * mean(pp) + 0.5 * mean(prep) + topFiveBonus`, where `topFiveBonus = sum over elders of (5 - position) * 4` for books in that elder's ordered top five (so a #1 vote is worth 16, a #5 vote worth 4).
- Selection: the top 10 fiction by composite form the Fiction shelf, the top 10 nonfiction form the Nonfiction shelf (each ranked 1-10 on its own shelf), and the next 50 by composite, fiction and nonfiction mixed, form the single ranking numbered 21 to 70. Total: 70 books.
- A book needs scores from at least 2 of the 3 elders to be ranked at all.

## Late additions protocol (single nominations)

When the owner or a reader nominates a book between full rounds, do not re-run the whole council. Instead:

1. One research agent builds a full entry under the same verification rules, including an honest rationale (if the case is weak, the rationale says so; the elders decide).
2. Each elder scores the nomination against calibration anchors drawn from that elder's OWN previous scores (a spread from their top book to their lowest), with an explicit instruction not to inflate late arrivals.
3. The nomination gets no top-five bonus. Its composite is `0.5 * mean(pp) + 0.5 * mean(prep)`.
4. It enters the 70 only if its composite beats the current #70's composite; the displaced book leaves. Either way it counts in the "books considered" total.

Precedent: in the last such sitting, seven nominations (two Iain M. Banks Culture novels, The Infinity Machine, Deep Utopia, Prediction Machines, A Fire Upon the Deep, A Closed and Common Orbit) were scored this way; only Prediction Machines cleared the cutoff. Nominations that fail are recorded as considered, and the owner is fine with nominated books not making it. The net matters more than the outcome.

## Standing editorial rulings (owner decisions; do not relitigate)

1. **AI Snake Oil (Narayanan and Kapoor) is permanently excluded from the list.** The owner read it, judged it contrary to the mind-expanding mandate, and removed it. It still counts among books considered. Warning from experience: research agents keep trying to re-nominate it because it appears on many external best-of lists. Strip it from any docket before the elders see it.
2. **No em-dashes anywhere** in prose the site publishes or in text written to the owner. The single exception is verbatim review quotes and official book titles or subtitles, which are never altered (prefer an edition whose subtitle uses an en-dash where one exists).
3. **Review quotes are sacred.** Word for word from the cited source, always.
4. **All published prose is plain language** at a high school reading level. Profound thought, effortless wording.
5. **The page never describes internal machinery.** No mention of research agents, rounds, workflows, or prompts. The only process concept the public page uses is the council of three elders (Historian, Builder, Sage), introduced in two plain sentences in the "How the books were chosen" box.
6. **Fiction is protected.** The elders lean nonfiction when everything competes in one pool; the two-shelf structure exists so stories are ranked against stories. Do not collapse the shelves back into one list.
7. The nonfiction shelf is labeled "The ten best true books, ranked" (not "forecasts": some entries are biographies or histories).

## Data schema (`canon-data.json`)

Top level: `fiction` (array of 10), `nonfiction` (array of 10), `rest` (array of 50, in rank order 21-70), `elder_notes` (array of `{elder, note, top_five}` for historian/practitioner/sage), `total_candidates` (int; currently 156).

Each book object: `title`, `author`, `year` (int), `kind` ("fiction" | "nonfiction"), `isbn13` (digits only, may be empty), `synopsis` (plain, 2-3 sentences), `why_it_matters` (plain, 3-6 sentences), `predictive_rationale` (the original case; kept for the record, not rendered), `key_predictions` (array of short plain sentences), `reviews` (array of `{quote, source}`, 2-4, verbatim), `elder_verdicts` (array of 3 plain sentences, order: Historian, Builder, Sage), `predictive_power` (int), `preparation_value` (int), `composite` (float, determines order).

## The page

Generated entirely by `build_canon_page.py`. Key facts for maintainers:

- **Covers** are fetched at build-prep time and inlined as base64 (about 180px wide, 10-30KB each). Fetch order with retries and a JPEG sanity check (magic bytes, >2KB): Open Library by ISBN (`covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false`), then Open Library search API for a `cover_i` id, then Google Books (`books.google.com/books/content?vid=ISBN{isbn}&printsec=frontcover&img=1`), then Penguin Random House (`images.penguinrandomhouse.com/cover/{isbn}`). Open Library throws transient 502s; always retry.
- **Theme**: light is the default regardless of OS setting; a prominent labeled pill (top right, fixed) toggles dark. Light tokens: page background `#edece7` (deliberately darker than the cards so they pop), card surface `#fcfcfb`, predictive-power bars blue `#2a78d6`, preparation bars orange `#eb6834`. Dark tokens are their stepped counterparts in the CSS `:root[data-theme="dark"]` block.
- **Interaction**: every card is clickable (role=button, Enter/Space work) and opens a modal with the large cover, both score bars, synopsis, why it matters, predictions, all review quotes, and all three verdicts. Hover affordance is a lift plus strong shadow plus a "Click for the full story" hint. The modal pulls the cover from the card's own img so the base64 is never duplicated.
- **Top Shelf**: fiction and nonfiction columns with per-rank height syncing (JS, two-column widths only) so row N aligns with row N, and small sticky column labels that pin to the top during scroll.
- **The Next 50**: five-column grid (3/2/1 columns at smaller widths), numbered 21-70, with fiction/nonfiction filter chips scoped to this section only.
- Also on the page: the "How the books were chosen" and score-explanation box, a stat line (books, considered, years covered, fiction/nonfiction split), Advice From the Elders, and a collapsible full-ranking table.

## Update playbooks

**A. Reader nominates a book:** follow the late additions protocol above, then playbook D.

**B. Periodic re-score (recommended roughly yearly):** predictions keep resolving, so predictive_power ages. Re-convene the three elders on the full pool in one sitting (fresh scores, same personas, same output schema), recompute composites and selection, run Plain Words on any new entrants, then playbook D. Expect real movement; that is the point.

**C. Full new round (expanding the pool):** new research agents with fresh beats and the current full title list to avoid duplicates, then a complete elder re-judging of old plus new together (never merge scores across separate sittings except via the calibration-anchor protocol), then Plain Words, then playbook D. Update `total_candidates`.

**D. Rebuild and QA (after any data change):** regenerate covers for new entries, run `build_canon_page.py`, then verify in a headless browser before publishing: exactly 70 card images and none broken (scroll the full page first; images lazy-load), no horizontal overflow, top-shelf rows aligned within a couple of pixels, modal opens and closes (click, Enter, Escape, backdrop), filter chips work, dark toggle works. Then audit: search the HTML for em-dashes (only verbatim quotes and official titles may contain them) and confirm AI Snake Oil is absent. Spot-check two or three review quotes against their sources.

**E. Pure page tweaks** (copy, colors, layout): edit `build_canon_page.py`, rebuild, run the QA checks. Never edit the generated HTML directly; it will be overwritten.

## History

- **Round 1** (July 2026): 5 research agents (modern era, classics, near-future society, nonfiction, wildcards), 54 candidates, 3 elders, top 25 published. #1: The Alignment Problem.
- **Round 2**: 5 expansive-mandate agents (minds, explainers, intimacy, civilizations, outliers), pool 98, full re-judge. #1: Empire of AI. Owner demoted AI Snake Oil from #4; all prose moved to plain language; process talk removed from the page.
- **Round 3**: restructure to 70 (two top-10 shelves plus 50 mixed). No new judging needed; the round-2 sitting had scored all 98.
- **Round 4**: 5 sourcing agents (lists, references, blogs, fiction, adjacent fields), pool 149, full re-judge with the expand-minds mandate explicit. AI Snake Oil permanently excluded. Fiction gained Feed and Blindsight; nonfiction gained Seeing Like a State (#4) and The Unaccountability Machine (#7).
- **Round 5**: seven late nominations scored under the calibration-anchor protocol; Prediction Machines entered at #56, displacing Out of Control. Pool 156. Current published state.

Scores in the current data reflect the world as of July 2026. When you re-score, update the footer line on the page that says so.
