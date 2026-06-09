# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers **campus survival and student life at Williams College** — specifically the knowledge that is genuinely hard to find through official channels: what the dorms are actually like to live in, when to do laundry so you don't compete with everyone else, how brutal the Williamstown spring weather really is, what students wish they had known before arriving, and what the real social and belonging experience feels like on a small, isolated rural campus.

Williams' official website answers logistics — dining hours, orientation schedules, handbook policies — but it communicates none of the lived experience. That experiential knowledge lives in scattered student writing: Her Campus opinion pieces, the student newspaper, Reddit, and unofficial wikis. A retrieval system that combines the practical official facts with authentic student voice is genuinely more useful than either source alone, because the questions a new student actually has ("what do I do when I'm homesick?" or "when is the laundry room not crowded?") are not answered on the admissions page.

---

## Document Sources

All 11 documents were collected on 2026-06-09 and saved as cleaned plain-text files with a source/title header in `documents/`.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Wikipedia — Williams College | Encyclopedia | en.wikipedia.org/wiki/Williams_College → `documents/01-wikipedia-williams-college.txt` |
| 2 | Williams Dining Services | Official practical | dining.williams.edu → `documents/02-dining-services.txt` |
| 3 | Dean's first-year letter to families | Official advice | families.williams.edu → `documents/03-first-year-families-letter.txt` |
| 4 | Her Campus — "Some Words of Wisdom" | Student voice | hercampus.com/school/williams → `documents/04-hercampus-some-words-of-wisdom.txt` |
| 5 | Her Campus — "Advice to My Younger Self" | Student voice | hercampus.com/school/williams → `documents/05-hercampus-advice-to-my-younger-self.txt` |
| 6 | Her Campus — "Five Secrets for Keeping Your Room Clean" | Student voice | hercampus.com/school/williams → `documents/06-hercampus-keeping-your-room-clean.txt` |
| 7 | Her Campus — "Managing Homesickness During Break" | Student voice | hercampus.com/school/williams → `documents/07-hercampus-managing-homesickness.txt` |
| 8 | Her Campus — "Healthy Bites – College Edition" | Student voice | hercampus.com/school/williams → `documents/08-hercampus-healthy-bites.txt` |
| 9 | Her Campus — "Why the Spring Weather is False Hope" | Student voice | hercampus.com/school/williams → `documents/09-hercampus-spring-weather-false-hope.txt` |
| 10 | Williams Student Handbook | Official policy | dean.williams.edu/student-handbook → `documents/10-student-handbook.txt` |
| 11 | First Days 2026 orientation schedule | Official practical | first-year.williams.edu/firstdays-schedule → `documents/11-first-days-orientation-schedule.txt` |

**Note on sourcing:** The most candid student channels — Reddit r/WilliamsCollege, Niche reviews, the Williams Record (student newspaper), and WSO "Willipedia" — all returned HTTP 403 or timed out during automated collection. This was verified by test-fetch before committing to the domain. The corpus therefore pairs Her Campus student-written articles (the most fetchable source of authentic student voice) with official pages for practical facts.

---

## Chunking Strategy

Documents were cleaned at collection time (navigation text, headers, and boilerplate stripped at the WebFetch stage), so the ingestion step only normalizes whitespace — it does not re-clean already-clean text.

**Chunk size:** ~800 characters (~150–200 tokens), split on paragraph and sentence boundaries. A chunk never begins or ends mid-sentence.

**Overlap:** ~120 characters (~15%) carried from the end of one chunk into the next.

**Why these choices fit your documents:** The corpus is deliberately mixed: short list-structured Her Campus tips (~300–700 words total), dense fact-packed pages (dining hours, orientation schedule), and longer prose (Wikipedia, the dean's letter). A fixed character cut would split a dining hall's name from its hours or a numbered tip from its list. Splitting on sentence/paragraph boundaries keeps each atomic idea intact. The 800-character target is large enough to hold one complete idea — a full dining hall block with all meal periods, or an entire numbered advice tip — but small enough that a retrieved chunk is mostly *about* the query rather than diluted by unrelated text, which would drag down cosine similarity. The 15% overlap is insurance for the longer prose documents where a single point spans two paragraphs; without it, a chunk boundary could orphan the second half of an argument.

ChromaDB was configured with cosine distance (`hnsw:space: cosine`) rather than the default L2, because `all-MiniLM-L6-v2` produces unit-normalized embeddings and cosine distance is the correct metric for them. Using L2 produced distance values above 1.0 that made the recommended 0.6–0.7 weak-match threshold meaningless.

**Final chunk count:** 72 chunks across 11 documents (avg 717 chars/chunk, min 210, max 1280).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional, 256-token max context). Chosen because it runs locally and free, is fast enough to embed the full 72-chunk corpus in under 10 seconds on a laptop, and is a well-validated general-purpose semantic search model — appropriate for a small, English-only corpus where we do not want API cost or rate limits during development.

**Production tradeoff reflection:** Deploying this for real users would shift several decisions:

- **Accuracy and context length:** `all-MiniLM-L6-v2` truncates at 256 tokens (~1,000 chars). Chunks that approach or exceed this are silently truncated before embedding, which was confirmed to degrade retrieval quality when chunk size was raised to 1,200 chars. A larger model — OpenAI `text-embedding-3-large`, Voyage `voyage-3`, or `bge-large-en` — handles longer sequences and captures finer semantic distinctions, which would matter for dense policy-text retrieval (e.g. Q5, where two different policy facts live close together in the handbook).
- **Multilingual support:** Williams students arrive "from more than 80 countries." A multilingual model (`multilingual-e5-large`, Cohere `embed-multilingual-v3`) would let non-English-speaking students query in their first language. MiniLM is English-only.
- **Local vs. API:** Local models (MiniLM, BGE) carry no per-query cost, no data leaves the machine (a privacy win for student-authored content), and there are no rate limits. API embeddings (OpenAI, Cohere, Voyage) deliver higher quality and require no GPU, but add cost per query, latency, and a data-sharing concern. For student-generated content this tradeoff matters.
- **Production pick:** For this domain (small, English, privacy-sensitive student voice), `bge-large-en` would be my production choice — meaningfully better retrieval than MiniLM, still fully local, no API or privacy concerns.

---

## Grounded Generation

**System prompt grounding instruction:**

The system prompt passed to `llama-3.3-70b-versatile` reads:

> You are a helpful guide for Williams College student life.  
> You must answer questions using ONLY the source excerpts provided below.  
> Do not use any prior knowledge, general knowledge, or information outside these excerpts.  
>
> Rules:  
> 1. Cite sources inline using [Source N] — e.g. "Mountain Day is in October [Source 1]."  
> 2. If the answer is spread across multiple sources, cite each one where relevant.  
> 3. If the provided excerpts do not contain enough information to answer the question, respond with exactly: "The documents don't cover this topic." Do not guess, infer beyond the text, or answer from general knowledge.  
> 4. Be concise — answer the question directly using the source text.

The model also receives `temperature=0` to eliminate creative variation that might introduce off-source content. The user message contains the numbered, labelled source excerpts as the only input — there is no other content in the prompt from which the model could draw facts.

**How source attribution is surfaced in the response:**

Source attribution is **programmatically guaranteed** — it does not depend on the model behaving correctly. After generation, `src/generate.py` builds the `sources` list directly from the retrieved-chunk metadata (deduplicated by title, ordered by retrieval rank) and returns it alongside the model's answer. Even if the model refused to cite anything, or cited incorrectly, the source list in the API response and UI would still accurately reflect which documents were retrieved and passed as context. In the Gradio UI, the sources box is populated from this programmatic list, and the chunks inspector shows the raw retrieved text with its `doc_id` for full transparency.

---

## Evaluation Report

All 5 questions from planning.md were run through the live system on 2026-06-09. Responses are the actual model output, not paraphrased.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which dining hall is open the latest at night, and until what time? | Whitmans', late night until 1:00 am daily | "Whitmans' is the dining hall that is open the latest at night, running until 1:00 am every day of the week [Source 2, Source 4]." | Partially relevant — correct dining chunk retrieved at rank 2; orientation schedule (rank 1) was a false positive | Accurate |
| 2 | What is Mountain Day at Williams and what do students do? | President cancels classes, first 3 Fridays in October, hike Stony Ledge, donuts/cider/a cappella | "Mountain Day is a tradition where the president cancels classes on one of the first three Fridays in October. Students hike up Stony Ledge, where they celebrate with donuts, cider, and a cappella performances [Source 1]." | Relevant — Wikipedia Mountain Day chunk at rank 1 (score 0.43) | Accurate |
| 3 | What's the best time to do laundry in the dorms, according to students? | A free weekday afternoon or late morning (avoid nights/weekends when it's crowded) | "The best time to do laundry is during nights, weekends, or when you have a free afternoon or late morning, as these are times when the machines are less busy." | Relevant — correct Her Campus chunk at rank 1 (score 0.37) | Inaccurate |
| 4 | What should a new student expect from spring weather in Williamstown? | Early warm days are "false hope," cold/rain through March–April, bring umbrella/jacket/boots | "Rain, cold, and wind, with the temperature likely to cool down, and the sun not shining for at least another two months. Not to be misled by warm days — they are only 'false hope.' Prepare with umbrellas, jackets, and boots [Source 1, Source 3]." | Relevant — all 4 chunks from the spring-weather article (scores 0.32–0.46) | Accurate |
| 5 | What is Williams' policy on hard alcohol and large parties? | Hard alcohol and kegs prohibited; parties over 20 must be registered; medical amnesty applies | "Williams prohibits hard alcohol and common source alcohol (kegs, punch, etc.). Parties over 20 people require registration [Source 1, Source 2]." (medical amnesty omitted) | Relevant — handbook chunks at ranks 1–2 (scores 0.36, 0.38) | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Q3 — "What's the best time to do laundry in the dorms, according to students?"

**What the system returned:** "The best time to do laundry in the dorms is during nights, weekends, or when you have a free afternoon or late morning, as these are times when the machines are less busy."

**Root cause (tied to a specific pipeline stage):** This is a **generation-stage failure**, not a retrieval failure. Retrieval worked correctly — the exact relevant chunk was at rank 1 with the best cosine score of any query in the evaluation (0.37). The chunk contained the correct advice verbatim.

The source text reads: *"Nights and weekends are a common time to do laundry; do you have a free afternoon one day or a late morning on another? Those are great times to take advantage of the empty machines."*

The sentence structure is contrastive: "nights/weekends = when everyone does it (crowded)" vs. "free afternoon or late morning = the recommended alternative." The model misread this as a list of equally valid times and merged the two into a single recommendation, inverting the actual advice. The LLM treated the contrast as conjunction.

This type of error — misreading a contrastive sentence structure where the first clause establishes a negative condition and the second provides the correction — is a known failure mode for instruction-tuned language models on pragmatic reasoning. The model extracted the surface entities (nights, weekends, free afternoon, late morning) without resolving the rhetorical relationship between the clauses.

**What you would change to fix it:** Two approaches. First, restructure the source document so the contrast is explicit: *"Avoid nights and weekends — that's when machines are crowded. Use a free weekday afternoon or late morning instead."* Clearer markup in the document reduces the ambiguity the model has to resolve. Second, at the generation stage, add a verification instruction to the system prompt: *"If the context uses contrast words ('but', 'instead', 'rather than'), make sure your answer captures which option is recommended, not just list all the mentioned options."* A post-generation self-check could also catch this: ask the model to confirm its answer against the source text before outputting.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The planning.md architecture diagram — built before any code — directly determined the file structure. Each box in the ASCII diagram became exactly one module: `src/ingest.py`, `src/chunk.py`, `src/store.py`, `src/retrieve.py`, `src/generate.py`. When debugging retrieval during Phase 3, the diagram made it immediately obvious which stage to isolate: "retrieval is returning a false positive at rank 1" pointed to `src/retrieve.py` and `src/store.py`, not to `src/ingest.py` or `src/generate.py`. Without that pre-committed structure, debugging a five-stage pipeline would have required understanding all the code at once.

**One way your implementation diverged from the spec, and why:**

The spec committed to ChromaDB's default distance metric without specifying which one. During implementation it became clear that ChromaDB defaults to L2 (Euclidean) distance, which produces values well above 1.0 for `all-MiniLM-L6-v2` embeddings. The recommended 0.6–0.7 weak-match threshold in the assignment assumes cosine distance (range 0–1). Running with L2 made all retrieved scores look "weak" even when retrieval was working correctly, and made the threshold-based debugging advice impossible to apply. The fix — adding `metadata={"hnsw:space": "cosine"}` to the `create_collection` call — was not in the spec because it's an implementation detail of the library rather than a design decision. This kind of discovery is exactly why specs should leave implementation details to the code.

---

## AI Usage

**Instance 1 — Generating the ingestion + chunking pipeline from the spec**

- *What I gave the AI:* The full Chunking Strategy section of planning.md (800 chars, 120 overlap, sentence/paragraph-aware, must not split a dining hall from its hours or a numbered tip from its list), plus a description of two contrasting document structures: the dense dining hours page and the short Her Campus list articles.
- *What it produced:* `src/ingest.py` with `load_documents()` that parsed the SOURCE_URL/TITLE header into metadata and a `clean_text()` that collapsed whitespace, and `src/chunk.py` with a `chunk_text()` function that split on paragraph boundaries first, then sentence boundaries, packing up to 800 chars with 120-char overlap.
- *What I changed or overrode:* The initial chunker used a fixed-character split with a sentence-boundary fallback. I directed it to invert the logic — paragraph boundaries are the primary split point, sentence boundaries are the fallback within a paragraph, and hard character splits are only used when a single sentence exceeds the limit. This change was necessary because the dining document's structure (hall names as headings, hours as bullet lists) has no sentence boundaries inside the hour blocks — the original approach would have split `### Whitmans'` from `- Monday–Friday: Late Night 9:30 pm–1:00 am`, exactly the failure mode the spec called out.

**Instance 2 — Debugging the retrieval distance metric**

- *What I gave the AI:* The score output from the first retrieval test run (all scores in the 0.75–0.97 range despite some results being clearly relevant), the ChromaDB collection creation code, and the assignment's guidance that "scores above 0.6–0.7 indicate weak matches."
- *What it produced:* An analysis identifying that ChromaDB's default L2 metric produces values outside the 0–1 range assumed by the 0.6–0.7 threshold, and a one-line fix adding `metadata={"hnsw:space": "cosine"}` to the `create_collection` call. After rebuilding the index, scores dropped to 0.31–0.49 and the threshold guidance became meaningful.
- *What I changed or overrode:* The AI also suggested increasing chunk size to 1,200 characters to improve semantic density. I tested this first, found that scores got *worse* (not better) at 1,200 chars, and diagnosed the reason: `all-MiniLM-L6-v2` truncates at 256 tokens (~1,000 chars), so chunks above that limit are silently truncated before embedding, losing the information that was supposed to make the embedding richer. I overrode the chunk-size suggestion and kept 800 chars, applying only the metric fix.
