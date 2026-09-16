# Brief: redraw the five figures in Can Artificial Minds Feel? (one build, one check with fixes, then stop)

File: `/Users/pundir/Claud/Artificial Minds/Final website/can-artificial-minds-feel/can-artificial-minds-feel.html` (about 310 KB; most of it is base64 portraits, do not print it whole). Backup already made: `_history/before-figures-16-sep-2026.html`. Read `/Users/pundir/Claud/Artificial Minds/CLAUDE.md` first, then the five `<figure>` blocks with `.plate-frame` SVGs (Figures 1 to 5) and the CSS for `.plate-frame`, `.plate-frame svg text`, `figcaption`, `.fig-no`. Change only those five SVGs, their `aria-label`s, and the small CSS block for figure text. Captions and prose stay as they are.

Pundir's verdict: "text is going outside boxes, the labels are misaligned and not properly justified. All the illustrations need to be rethought for clarity and should be professionally done visually." Two labels he called out as unclear or as slogans: "THE ONE A USER MEETS", "A IS ALREADY GONE", "ONE FLASH PER REPLY. BETWEEN THEM, NOTHING RUNS", "WHAT PRODUCTS CALL MEMORY IS A NOTE SOMETHING ELSE WROTE AND CARRIED FORWARD".

## Rules for all five

- This is a light page: paper `#f8f5ee`, tint `#f1ecdf`, ink `#1b1813`, ink-soft `#4a453c`, ink-faint `#6f6857`, ink-ghost `#a29a88`, rule `#d5cdba`, rubric `#8c2a1a`. Use these and nothing else. Line weights 1 to 1.4 px for outlines, 5 to 6 px for the bars that stand for lines of text.
- Two text styles, defined once as classes in the CSS (replace the current `.plate-frame svg text` rule): `.pt` for short tags in the page's letter-spaced small caps (`font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;fill:#6f6857`) and `.ps` for sentences (`font-size:12.5px;letter-spacing:.01em;fill:#4a453c`, normal case). A `.pr` modifier sets `fill:#8c2a1a`. All text keeps the page's serif family through the existing rule.
- Every label sits inside its box with at least 10 units of padding on every side, or clearly outside the box with at least 8 units of clearance. Nothing overlaps a line, bar or circle. Box widths are chosen after the text, never before. Centred text is centred on its box; left-aligned text shares one left edge inside the box.
- One closing sentence at the bottom of each figure, in `.ps`, plain English, no slogan, no "X, not Y".
- viewBox width stays 640; height whatever the drawing needs. `role="img"` and a plain `aria-label` that says what the picture shows.

## The five, with the words decided

Figure 1 (one model, many instances). Top: a wide box labelled inside, `.pt`, "The model, frozen since its training ended". Below it a row of five small boxes labelled inside `.pt` "instance"; the fourth outlined in rubric with a `.ps.pr` line under it: "The user talks to this instance." Thin lines from the model box to each instance box (a stamp, or a copy). Closing sentence: "Every chat gets a fresh instance of the same model."

Figure 2 (two turns of one chat). Left box titled above in `.pt` "Turn 1". Inside: three text bars, the first in rubric, and a circle-and-tag row inside the box, `.ps`: "Instance A writes the reply". Under the box, `.ps.pr`: "The reply was wrong." Between the boxes a dashed arrow and the tag `.pt` "a copy of the chat". Right box titled "Turn 2". Inside: the same three bars faded, a fourth bar in rubric, the words `.ps.pr` "this is wrong" under that bar, and the row "Instance B reads the chat and the complaint". Under the box, `.ps`: "Instance A no longer exists." Closing sentence: "The instance that reads the complaint is a different instance from the one that made the mistake."

Figure 3 (a stream against flashes). Two rows. Row 1 tag `.pt` "A human, as humans experience it", a continuous band. Row 2 tag "An AI instance", five short flashes with gaps. A time arrow along the bottom with the tag "time". Closing sentence: "An instance runs only while it writes a reply. Between replies, nothing runs."

Figure 4 (memory across chats). Three windows in a row, titled above in `.pt`: "Monday's chat, ended", "Tuesday's chat, ended", "Today's chat, starting". In the first two, a small note icon at the corner with the tag `.pt` "the app's notes" (once, over the first). In the third, a rubric bar at the top with `.ps.pr` under it: "The app pastes its notes in first." Arrows from the two note icons to the third window's top. Closing sentence: "What products call memory is a note the app wrote about earlier chats and pasted into the new one."

Figure 5 (the overlap). Two circles with tags "A human" and "An artificial mind" placed outside the circles where they cannot touch a stroke; the lens tinted; under it `.ps`: "What can honestly be said about both." Keep the shape; fix the placement.

## Check once, fix, then stop

Render with the sandbox browser (playwright, `chromium.launch(args=["--no-sandbox"])`, with `LD_LIBRARY_PATH=~/.cache/ms-playwright/chromium_headless_shell-1234/chrome-linux` and `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`), screenshot each `.plate-frame` at 1100 px and 390 px into `/sessions/dreamy-sweet-faraday/mnt/outputs/`, and read every picture. Also run this check in the page and fix anything it reports: for every `<text>` in the five SVGs, `getBBox()` must lie inside the SVG's viewBox, and must not intersect the `getBBox()` of any `rect`, `line`, `circle` or `path` in the same SVG unless that text is inside a `rect` with the padding above (report the pairs). Tag balance on the file, 0 em-dashes. One fix pass, then stop. Verify size and md5sum through the /Users/pundir path. Do not spawn agents. Do not call WebSearch. Report in eight lines.
