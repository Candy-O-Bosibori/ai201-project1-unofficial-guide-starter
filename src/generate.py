"""Stage 5 — Grounded generation.

Sends retrieved chunks to Groq's llama-3.3-70b-versatile and returns an
answer grounded strictly in those chunks. Source attribution is programmatically
guaranteed — the source list is always built from retrieved-chunk metadata and
appended to the response regardless of what the model says.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

# The system prompt enforces grounding structurally, not just by suggestion.
# The model is given numbered, labelled sources and told exactly what to do
# when the context does not contain the answer.
SYSTEM_PROMPT = """\
You are a helpful guide for Williams College student life.
You must answer questions using ONLY the source excerpts provided below.
Do not use any prior knowledge, general knowledge, or information outside these excerpts.

Rules:
1. Cite sources inline using [Source N] — e.g. "Mountain Day is in October [Source 1]."
2. If the answer is spread across multiple sources, cite each one where relevant.
3. If the provided excerpts do not contain enough information to answer the question,
   respond with exactly: "The documents don't cover this topic."
   Do not guess, infer beyond the text, or answer from general knowledge.
4. Be concise — answer the question directly using the source text.\
"""


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered, labelled context block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {chunk['title']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)


def generate(question: str, chunks: list[dict]) -> dict:
    """Generate a grounded answer from retrieved chunks.

    Returns:
        answer  – model's response (with inline [Source N] citations)
        sources – programmatic list of unique source titles from retrieved chunks
                  (always present, never depends on model output)
        chunks  – the chunks passed to the model (for evaluation/debugging)
    """
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    context = _build_context(chunks)
    user_message = f"Context:\n\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,          # deterministic — no creative wandering off-source
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    # Programmatic source list — built from chunk metadata, not model output.
    # Deduplicates by title while preserving retrieval order.
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        key = chunk["title"]
        if key not in seen:
            seen.add(key)
            sources.append(key)

    return {"answer": answer, "sources": sources, "chunks": chunks}
