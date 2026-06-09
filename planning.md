# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**Campus survival & student-life guide for Williams College** — what daily life is actually like
for an undergraduate: dorm living, dining, weather, adjusting socially and academically, traditions,
and the unwritten coping advice (homesickness, room cleaning, eating well, belonging) that the
admissions website never tells you.

This knowledge is valuable because Williams' official channels describe *policies and logistics*
(dining hours, the handbook, the orientation schedule) but not the *lived experience* — what students
wish they'd known, what the New England spring is really like, or how it feels to belong (or not) on a
small, intense, rural campus. That experiential knowledge lives in scattered student writing (Her Campus
articles, the student newspaper, Reddit) that's hard to find, hard to search, and not consolidated
anywhere. A retrieval system that blends the practical official facts with authentic student voice is
genuinely more useful than either source alone.

**Note on sources:** the most candid student channels (Reddit r/WilliamsCollege, Niche reviews, the
Williams Record, the WSO "Willipedia" wiki) block automated fetching. The corpus therefore pairs
fetchable student-written articles (Her Campus) with official practical pages (dining, handbook,
orientation, the dean's first-year letter) and Wikipedia for traditions/campus facts.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

All sources collected on 2026-06-09 and saved as cleaned `.txt` files (with a source/title header) in `documents/`.

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Wikipedia — Williams College | Campus, traditions (Mountain Day, Trivia, purple cow), athletics (Ephs, NESCAC) | en.wikipedia.org/wiki/Williams_College → `documents/01-wikipedia-williams-college.txt` |
| 2 | Williams Dining Services | Dining halls, hours, late-night, mobile-ordering venues | dining.williams.edu → `documents/02-dining-services.txt` |
| 3 | Dean's first-year letter to families | Advice on community, courses, social life, asking for help | families.williams.edu → `documents/03-first-year-families-letter.txt` |
| 4 | Her Campus — "Some Words of Wisdom" | Student article; literary quotes for encouragement | hercampus.com/school/williams → `documents/04-hercampus-some-words-of-wisdom.txt` |
| 5 | Her Campus — "Advice to My Younger Self" | Senior's candid advice: belonging, procrastination, lab safety, balance | hercampus.com/school/williams → `documents/05-hercampus-advice-to-my-younger-self.txt` |
| 6 | Her Campus — "Five Secrets for Keeping Your Room Clean" | Dorm-life tips: laundry timing, vacuuming, dishes | hercampus.com/school/williams → `documents/06-hercampus-keeping-your-room-clean.txt` |
| 7 | Her Campus — "Managing Homesickness During Break" | Coping tips: reach out, explore campus, self-care | hercampus.com/school/williams → `documents/07-hercampus-managing-homesickness.txt` |
| 8 | Her Campus — "Healthy Bites – College Edition" | Late-night healthy snack recipes using the dining/salad bar | hercampus.com/school/williams → `documents/08-hercampus-healthy-bites.txt` |
| 9 | Her Campus — "Why the Spring Weather is False Hope" | New England / Williamstown weather reality check | hercampus.com/school/williams → `documents/09-hercampus-spring-weather-false-hope.txt` |
| 10 | Williams Student Handbook | Policy overview: housing, conduct, alcohol, honor code | dean.williams.edu/student-handbook → `documents/10-student-handbook.txt` |
| 11 | First Days 2026 orientation schedule | New-student orientation events day-by-day | first-year.williams.edu/firstdays-schedule → `documents/11-first-days-orientation-schedule.txt` |

**Structure observations (from skimming, to inform chunking in Milestone 2):**
- The Her Campus articles (#4–9) are **short, list-structured** pieces (~300–700 words), where each
  numbered tip is a self-contained idea. Key facts are concentrated in a sentence or two per item.
- The official pages (#2, #10, #11) are **dense and fact-packed** — dining hours, policy topics, and a
  timestamped schedule. A single chunk can hold many discrete facts, so retrieval must not split, e.g.,
  a dining hall's name away from its hours.
- Wikipedia (#1) and the dean's letter (#3) are **longer-form prose** with ideas spread across multi-
  sentence paragraphs, which argues for medium-sized chunks with overlap so a thought isn't cut in half.
- Implication: a moderate chunk size with overlap, split on paragraph/sentence boundaries, fits this
  mixed corpus better than a fixed character cut.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** ~800 characters (roughly 150–200 tokens), split on paragraph and sentence
boundaries — a chunk never starts or ends mid-sentence. Long paragraphs are packed up to ~800 chars;
short list items (e.g. a single numbered Her Campus tip) stay whole even if well under the target.

**Overlap:** ~120 characters (~15%) carried from the end of one chunk into the next.

**Reasoning:** The corpus is mixed (see structure notes above), so a fixed character cut is wrong for
it. 800 chars is large enough to keep one complete idea intact — a full numbered tip, a dining hall with
all its hours, one Wikipedia tradition — but small enough that a retrieved chunk is mostly *about* the
query rather than diluted by unrelated text (which would drag down the embedding similarity). Sentence-
boundary splitting prevents the classic failure where "Whitmans'… Late Night" lands in one chunk and
"9:30 pm–1:00 am" in the next. The 15% overlap is insurance for the longer prose docs (Wikipedia, the
dean's letter) where a single thought spans two paragraphs — overlap means the boundary doesn't orphan
half of it. We keep overlap modest because most of our key facts are short and self-contained, so heavy
overlap would just inflate the chunk count and retrieve near-duplicates.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional embeddings).
Chosen because it runs **locally and free**, is fast enough to embed the whole corpus in seconds on a
laptop, and is a well-proven general-purpose semantic-search model — appropriate for a small English-only
corpus where we don't want an API key or per-call cost just to prototype.

**Top-k:** 4 chunks per query. Enough to cover a fact that's spread across two chunks (or a question that
touches two docs) without flooding the LLM's context with low-relevance text that invites it to wander
off-source.

**Production tradeoff reflection:** If this were a real product and cost weren't the constraint, the
choice changes along several axes:
- **Accuracy / context length:** `all-MiniLM-L6-v2` truncates at 256 tokens and is a small model. A
  larger model (e.g. OpenAI `text-embedding-3-large`, Voyage `voyage-3`, or `bge-large`) captures more
  nuance and handles longer chunks, which would let us raise chunk size and lose fewer cross-sentence facts.
- **Multilingual:** our students come "from more than 80 countries" — if users asked questions in other
  languages, a multilingual model (`multilingual-e5-large`, Cohere `embed-multilingual-v3`) would matter.
- **Local vs API:** local (MiniLM, BGE) means no per-query cost, no data leaving the machine (a privacy
  win for student content), and no rate limits — but you own the GPU/latency. API embeddings (OpenAI,
  Cohere, Voyage) are higher quality and zero-ops but add cost, latency, and a data-sharing concern.
- **Latency:** at query time the embedding call is tiny either way; the bigger production cost is
  re-embedding the whole corpus when you change models, which favors a model you won't need to swap.
For this domain (small, English, privacy-sensitive student voice) a strong **local** model like
`bge-large-en` would be my production pick — better accuracy than MiniLM, still no API/cost/privacy issues.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

Each question is answerable from a specific document, and the five together span the corpus
(official facts, traditions, student-voice advice). Expected answers are the ground truth we'll grade
the system against in Milestone 6.

| # | Question | Expected answer | Grounding doc |
|---|----------|-----------------|---------------|
| 1 | Which dining hall is open the latest at night, and until what time? | Whitmans' is the only hall with late-night service, open until **1:00 am every day** (late night 9:30 pm–1:00 am). | `02-dining-services.txt` |
| 2 | What is Mountain Day at Williams and what do students do? | On one of the first three Fridays in October the **president cancels classes**; bells ring, the Outing Club unfurls a banner from Chapin Hall, and students **hike up Stony Ledge** to celebrate with **donuts, cider, and a cappella** performances. | `01-wikipedia-williams-college.txt` |
| 3 | What's the best time to do laundry in the dorms, according to students? | When the machines **aren't busy** — a free weekday afternoon or late morning, rather than nights/weekends when everyone does it; and put clothes away right after the dryer. | `06-hercampus-keeping-your-room-clean.txt` |
| 4 | What should a new student expect from spring weather in Williamstown? | Early warm days are **"false hope"** — cold and rain continue through March and April in New England, so expect ~two more months of gray; bring an **umbrella, jacket, and boots**. | `09-hercampus-spring-weather-false-hope.txt` |
| 5 | What is Williams' policy on hard alcohol and large parties? | Williams **prohibits the abuse of alcohol**; **parties over 20 people must be registered**, and **hard alcohol and common-source alcohol (kegs, punch) are prohibited**. Medical amnesty applies when a student seeks help in an emergency. | `10-student-handbook.txt` |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Key facts split across a chunk boundary.** The dense official pages pack many discrete facts close
   together (dining hall names next to their hours; a numbered tip next to its heading). If a split lands
   between a fact and its anchor, retrieval returns half the answer — e.g. "Whitmans' is open late" without
   "until 1:00 am," or a tip's text without which list it belongs to. *Mitigation:* sentence/paragraph-aware
   splitting plus 15% overlap; this is also exactly the kind of thing the Milestone 6 failure analysis should probe.

2. **Official-voice vs. student-voice imbalance, and over-confident answers on thin evidence.** The corpus
   skews toward dense official pages (because the candid student channels — Reddit, Niche, the Record, WSO —
   block fetching), so for experiential questions ("is it lonely here?", "what's the social scene like?")
   retrieval may return only tangential student snippets, and a naive LLM would happily fill the gap with its
   general knowledge. *Mitigation:* a strict grounding prompt that must answer **only** from retrieved chunks
   and explicitly say when the documents don't cover something, rather than inventing an answer.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
  ┌─────────────────────┐
  │ 1. DOCUMENT          │   documents/*.txt  (11 cleaned files w/ source headers)
  │    INGESTION         │   src/ingest.py — load files, parse SOURCE/TITLE header into
  │                      │   metadata, strip header + collapse whitespace/boilerplate
  └──────────┬───────────┘
             ▼
  ┌─────────────────────┐
  │ 2. CHUNKING          │   src/chunk.py — ~800 chars, ~120 overlap, sentence/para-aware
  │                      │   each chunk keeps {source, title, doc_id, chunk_index}
  └──────────┬───────────┘
             ▼
  ┌─────────────────────┐
  │ 3. EMBEDDING +       │   sentence-transformers all-MiniLM-L6-v2  →  384-d vectors
  │    VECTOR STORE      │   stored in ChromaDB (persistent ./chroma_db)  [build_index.py]
  └──────────┬───────────┘
             ▼
  ┌─────────────────────┐
  │ 4. RETRIEVAL         │   src/retrieve.py — embed query, Chroma similarity search,
  │                      │   return top-k=4 chunks + scores + metadata
  └──────────┬───────────┘
             ▼
  ┌─────────────────────┐
  │ 5. GENERATION        │   src/generate.py — Groq LLM (llama-3.3-70b-versatile) with a
  │                      │   strict grounding prompt → grounded answer + source citations
  └─────────────────────┘
             ▲
        user query  ──────►  query.py (CLI interface)
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** Use Claude (Claude Code) as the coding assistant. *Input:* the
Documents structure notes and the Chunking Strategy section above (800 chars / 120 overlap / sentence-aware),
plus a sample of two contrasting docs (a list-style Her Campus article and the dense dining page). *Expect it
to produce:* `src/ingest.py` (`load_documents()` parsing the SOURCE_URL/TITLE header into metadata + a
`clean_text()` that collapses whitespace) and `src/chunk.py` (`chunk_text(text, size, overlap)` that respects
sentence/paragraph boundaries). *Verify:* run it, print the final chunk count and spot-check that no dining
hall is split from its hours and no numbered tip is orphaned from its list.

**Milestone 4 — Embedding and retrieval:** *Input:* the Retrieval Approach section (all-MiniLM-L6-v2, top-k=4,
ChromaDB persistent store) and the chunk objects from Milestone 3. *Expect it to produce:* `src/store.py`
(build/load a persistent Chroma collection, embed chunks with sentence-transformers, attach metadata),
`build_index.py` (one-shot ingest→chunk→embed→persist), and `src/retrieve.py` (`search(query, k)` returning
top-k chunks + similarity scores + source metadata). *Verify:* query "late night dining" and confirm the
top chunks come from `02-dining-services.txt`; query a few eval questions and eyeball that retrieval is on-target.

**Milestone 5 — Generation and interface:** *Input:* the Grounded Generation requirement and the Anticipated
Challenge #2 (don't let the model fill gaps from general knowledge). *Expect it to produce:* `src/generate.py`
(Groq client using `llama-3.3-70b-versatile`, a system prompt that forbids using anything beyond the retrieved
context and requires it to say when the docs don't cover the question, with chunks formatted as `[Source N: title]`
and a source-attribution list appended to every answer) and `query.py` (CLI: `python query.py "question"` →
prints answer, sources, and retrieved chunks). *Verify:* ask an in-corpus question (cites the right doc) and an
out-of-corpus question like "what's the tuition refund policy?" (system should refuse / say it's not in the sources).
