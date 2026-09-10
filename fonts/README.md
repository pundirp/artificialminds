# fonts

Every font the Artificial Minds pages may use, plus the one stylesheet that names
them. This folder sits at the root of the site, next to `index.html`.

Nothing here calls out to the network. The pages load these files and no others.

## The four families

A family is three roles used together. `text` is the reading face, for body
prose, headings, the italic subtitle and captions. `label` is a sans for small
uppercase letter-spaced labels. `mono` is a monospace for the text inside the
SVG figures, for code and for footer lines.

| id | text | label | mono | files | weight over the wire |
| --- | --- | --- | --- | --- | --- |
| `house` | system serif | system sans | system mono | 0 | nothing |
| `charter` | Charis SIL | Public Sans | Cousine | 7 | 251 KB |
| `brygada` | Brygada 1918 | Albert Sans | Sometype Mono | 7 | 112 KB |
| `bitter` | Bitter | Atkinson Hyperlegible | Spline Sans Mono | 7 | 149 KB |

When to use each one:

- **`house`** is for the index and the essays as they stand. It loads no files
  and waits for nothing. The reader sees their own device's serif.
- **`charter`** is the same feel as `house`, made identical on every device. Use
  it for essays and long reading, where the page should look the same for
  everyone.
- **`brygada`** is for fiction, poems and period pieces. An older, warmer letter
  with more voice in it.
- **`bitter`** is for guides and explainers. A sturdy slab that holds its shape
  at small sizes, paired with a label face built for easy reading.

A page loads only the files for the family it uses, because a browser fetches a
font file only when the page actually sets text in it.

`house` resolves to Iowan Old Style on Mac and iPhone, Palatino Linotype on
Windows, and Noto Serif on Android, with the platform sans and the platform
monospace for the other two roles.

## How a page adopts a family

Three lines, plus the link. Link the stylesheet, then point the page's own three
variables at one family:

```html
<link rel="stylesheet" href="fonts/fonts.css">
```

```css
:root {
  --serif: var(--family-charter-text, "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif);
  --sans:  var(--family-charter-label, -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif);
  --mono:  var(--family-charter-mono, ui-monospace, "SF Mono", Menlo, Consolas, monospace);
}
```

From a project folder one level down, the link is `../fonts/fonts.css`. The
`url()` paths inside `fonts.css` are relative to `fonts.css` itself, so the
folder works from any depth.

Swap `charter` for `house`, `brygada` or `bitter` and nothing else in the page
changes.

## What is in the folder

- `fonts.css`. Every `@font-face` rule first, then a `:root` block holding the
  twelve family variables. Nothing else. It sets no styles on any element.
- 21 `.woff2` files, named `<face-slug>-<weight>-<normal|italic>.woff2`, for
  example `charis-sil-400-italic.woff2`. 512 KB in total for all three hosted
  families, which no single page ever loads at once.
- `LICENSES/`. One licence file per face, copied from the source repository,
  named `<face-slug>-OFL.txt`. Every face here is under the SIL Open Font
  License 1.1, which allows use on a website and asks that the licence travel
  with the font. It also travels inside each file, in the font's name table.
- `manifest.json`. Machine readable. Every family, every role, every file, its
  size in bytes, the exact URL it came from, and any note about it.
- `fonts_preview.html`. A page that shows the families on the same sample text,
  so you can look and compare.

## Where the files came from

All nine faces come from the Google Fonts repository, from
`https://raw.githubusercontent.com/google/fonts/main/ofl/<directory>/`. Every
face named in the plan was there, and every weight asked for existed, so no face
and no weight was substituted.

Six of the faces ship only as variable fonts. Those were instanced to the exact
weight wanted with fontTools `instancer`, with any other axis pinned to its
default, before subsetting. The other three were taken as static files.

Each file was then subset with `pyftsubset` to Latin and the punctuation and
figure marks the site draws:

```

The fallback list inside each var() matters: if fonts.css ever fails to load, the page then falls to the site's system stacks instead of the browser default. Arrows in a label belong in the text face; none of the label faces carries them.

U+0000-024F, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2113,
U+2122, U+2190-2199, U+21B5, U+2212, U+2215, U+2248, U+2260, U+2264-2265,
U+2713, U+2717, U+25A0-25A1, U+25CF, U+2605-2606, U+FEFF, U+FFFD
```

These layout features were kept where the face has them: `kern`, `liga`,
`calt`, `onum`, `lnum`, `tnum`, `pnum`, `smcp`, `c2sc`, `ss01`, `case`. All name
records were kept, so the family name and the licence stay with each file. The
largest file is 54 KB and the smallest is 11 KB.

## The arrow and check marks

The site draws seven marks in its figures: `→ ← ✓ ✗ · × ≈`. Most of these faces
do not contain all of them, and nothing was added to any font to fix that.

Where a face lacks a mark, the browser takes that one character from the next
font in the stack, which is the matching system stack. The mark still appears,
in the reader's own system font, at the reader's own idea of its width. In a
line of figure text this shows up as one character that does not quite match.

- `·`, `×` and `≈` are in every face here.
- `✗` is in no face here.
- `✓` is only in Charis SIL.
- `→` and `←` are in Charis SIL, Cousine, Brygada 1918, Sometype Mono and
  Bitter. Public Sans, Albert Sans, Atkinson Hyperlegible and Spline Sans Mono
  lack them.

So the mono role gets real arrows in `charter` and `brygada`, and borrowed
arrows in `bitter`. `manifest.json` lists this per face under `marks_by_face`.

## Monospace widths

The site's SVG figures were drawn against a monospace 0.6 em wide. Cousine is
0.6001 em and Spline Sans Mono is 0.6, so `charter` and `bitter` match.

Sometype Mono, the mono of the `brygada` family, is 0.58 em. Lines set in it run
about 3 percent shorter than the same line in a 0.6 em mono. That is small, but
it is enough to shift a label in a tightly drawn figure.

## How to add a face

1. Find it in the Google Fonts repository under `ofl/<directory>/`. Read
   `METADATA.pb` there to see the file names, styles and weights it ships.
2. Download the TTF. If it is a variable font, instance it to the weight you
   want first.
3. Subset it with `pyftsubset` using the unicode range and the feature list
   above, with `--flavor=woff2` and `--name-IDs='*'`.
4. Name the result `<face-slug>-<weight>-<normal|italic>.woff2` and drop it in
   this folder.
5. Add an `@font-face` rule to `fonts.css` in the faces section, using the
   face's real family name.
6. Copy `OFL.txt` from the same repository directory into
   `LICENSES/<face-slug>-OFL.txt`.
7. If it is part of a new family, add the three `--family-<id>-*` variables to
   the `:root` block, each ending in the matching system stack.
8. Open the finished file with fontTools and check which of the seven marks it
   has, then record the file, its size, its source URL and its marks in
   `manifest.json`.
