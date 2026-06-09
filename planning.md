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

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
