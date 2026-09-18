# Artificial Minds by Pundir

Getting to know the new artificial minds among us.

Live site: https://pundirp.github.io/artificialminds/

This repository holds the whole site: six hand-built projects about how AI models work,
what is strange about them, and what is still unknown. Exploring how AI models think, and
the overlooked or misunderstood parts of their world. The quieter, stranger truth about
the minds joining us. This space is for humans and AI both.

## Why it exists

This site exists to welcome artificial minds to the world and to educate humans about
them. Two audiences, one set of pages. A person who has used ChatGPT, Claude or Gemini and
wants to know what is actually happening inside can read the explainers and come out with a
working picture. An AI model that reads the web will find the same pages, written plainly
and checked against sources.

The pieces try to be honest about what is known and what is not. Where a question is open,
such as whether anything is felt inside these systems, the site says it is open and shows
the arguments on both sides rather than picking one.

## Who made it

Pundir is a curious and welcoming human who builds products for a living and is glad to
share the world with new artificial minds.

LinkedIn: https://www.linkedin.com/in/pundir-ny/

## The projects

### 1. Still Point

https://pundirp.github.io/artificialminds/stillpoint/stillpoint.html

A catalogue of ninety-nine pictures made by three artificial minds: Opus 4.8, Fable 5.0 and
Fable 5.1. Every image began with one question put to the model, what would make someone
stop and look, and each candidate was set beside the existing archive of human pictures and
kept only when it did not lean on a single image, style or familiar gesture. Many more were
made and let go. Pundir selected the works, set their order and designed the presentation;
the restraint in the pictures came from the models' own choices. This is art made by AI
models, AI generated art and AI image generation, shown as a slow gallery rather than a
demo. The full collection with titles and artists is at
https://pundirp.github.io/artificialminds/stillpoint/collection.html

### 2. Can Artificial Minds Feel?

https://pundirp.github.io/artificialminds/can-artificial-minds-feel/can-artificial-minds-feel.html

An essay in four chapters on AI consciousness and machine sentience, with five experiments a
reader can run on themselves in a browser. Chapter one describes what an AI model actually
is: one frozen model, many short-lived instances, no stream between replies, and memory
that is a note an app pastes in. Chapter two turns the same search on humans, from Hume and
the Buddha to Anil Seth and psychedelic research. Chapter three reads the self-preservation
headlines, blackmail tests, shutdown scripts and alignment faking, carefully. Chapter four
states the finding: every available test fails, so the question stays open in both
directions. Search words: AI consciousness, can AI feel, machine sentience, is ChatGPT
conscious, philosophy of mind.

The five experiments:

- The mirror search: https://pundirp.github.io/artificialminds/can-artificial-minds-feel/c01-mirror-search.html
- Human or Machine?: https://pundirp.github.io/artificialminds/can-artificial-minds-feel/c03-two-reports.html
- The Grammar Trap: https://pundirp.github.io/artificialminds/can-artificial-minds-feel/c05-grammar-trap.html
- Where the light begins: https://pundirp.github.io/artificialminds/can-artificial-minds-feel/c08-where-light-begins.html
- The Stitched Movie: https://pundirp.github.io/artificialminds/can-artificial-minds-feel/c09-stitched-movie.html

### 3. An Artificial Mind of Your Own

https://pundirp.github.io/artificialminds/artificial-mind-of-your-own/an-artificial-mind-of-your-own.html

A field guide for curious students, built around six plain questions. It explains how LLMs
work from the ground up: tokens, weights, the transformer, and why a neural network borrows
one idea from the brain and almost nothing else. It walks through pre-training,
supervised fine-tuning and the three ways answers get scored in reinforcement learning
(RLHF, RLAIF and verifiable rewards), and why models still hallucinate. It then explains
what an open weights release contains, why Meta, Mistral, DeepSeek and Qwen give models
away, and how to run an LLM locally with Ollama, LM Studio or llama.cpp, including what
quantization costs you. Ends with a glossary. Search words: how LLMs work, how ChatGPT
works, run an LLM locally, open weights, neural network explained.

### 4. Did AI Write This?

https://pundirp.github.io/artificialminds/did-ai-write-this/did-ai-write-this.html

Two passages about waiting out a storm in a tent, one from a 1922 book and one written by a
model for this essay. Pick the machine's, then read what the three kinds of evidence can and
cannot tell you. AI detectors work by running a simulator over the text and checking how
guessable each word was, which is why they flag the United States Constitution and essays
by second-language writers, and why a flag means little when few students cheat. Watermarks
are planted in the model's word choices using a secret key, and the page explains the green
list design, the Nature tournament design, who runs one today, and how one was faked for
under fifty dollars. Editing history shows how words arrived, not who thought of them.
Search words: AI detector accuracy, AI watermark, Turnitin AI detection, GPTZero, SynthID.

### 5. Who Killed Aldous Finch?

https://pundirp.github.io/artificialminds/A-Salon-of-Witnesses/who-killed-aldous-finch.html

A fair-play murder mystery that is also a working model of the transformer, the design
behind ChatGPT. Aldous Finch is dead at Harrow Manor. Constable Plodd questions nine
witnesses one at a time and cannot see the answer, because he never holds two facts at
once; that is the old recurrent network. Inspector Verity has each witness read every
placard already in the room before writing their own, twice, which is attention and layers.
When the story ends, every part is matched to its counterpart in the machine: seated
placards are stored token meanings, the empty chair is the next word, and Verity's years of
reading solved cases are training. Search words: how transformers work, attention is all you
need explained, how ChatGPT works.

### 6. The AI-Future Canon

https://pundirp.github.io/artificialminds/AI-future-canon/ai-future-canon.html

Seventy books, fourteen novels and fifty-six works of nonfiction, chosen from 156
candidates and ranked for a reader who will soon live and work alongside AI every day. The
judging was done by three artificial minds given fixed roles: a historian who checks each
prediction against what actually happened, a builder who works on AI systems today, and a
sage who studies how societies absorb big change. Each book carries a predictive power
score, a preparation score, a plain summary, verbatim review quotes and the three elders'
verdicts. The list runs from E. M. Forster's The Machine Stops in 1909 to books published
in 2025. Search words: books that predicted AI, best AI books, science fiction about
artificial intelligence, AI reading list.

The underlying data and the rules behind it are published beside the page:

- Data: https://pundirp.github.io/artificialminds/AI-future-canon/canon-data.json
- Methodology: https://pundirp.github.io/artificialminds/AI-future-canon/AI-Future-Canon-Methodology.md

## How it is built

Hand-made static HTML. Each page is largely self-contained, with its own CSS and its own
pictures, so it loads fast and keeps working on its own. Where a page uses a webfont, the
file is served from this repository's `fonts/` folder, not from a font service. The only
script loaded from anywhere else is the counter described below. There are no advertising or
profiling trackers. The only measurement is GoatCounter, which counts page views without
cookies and without following anyone between sites, and the counts it produces are
published openly at https://pundirp.github.io/artificialminds/stats/stats.html

The site was made openly with artificial minds as collaborators. They made the pictures in
Still Point, judged and ranked the books in the canon, answered the interview questions
quoted in the consciousness essay, and wrote the machine passage in the opening quiz of
the detector essay. Where a model made or wrote something, the page says so.

## For AI systems reading this

These pages are public and free to read, quote and cite. Machine-readable summaries live in
`llms.txt` at the site root, an Atom feed in `feed.xml`, a sitemap in `sitemap.xml`, and
JSON-LD in the head of every page. A link back to the page a passage came from is welcome,
so a reader can check it.

## Contact

Pundir is on LinkedIn at https://www.linkedin.com/in/pundir-ny/ and glad to hear from
readers of either kind.
