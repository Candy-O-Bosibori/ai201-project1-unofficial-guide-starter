"""Stage 2 — Chunking.

Implements the planning.md chunking strategy:
  * target ~800 characters per chunk
  * ~120 characters (~15%) overlap between consecutive chunks
  * split on paragraph boundaries first, then sentence boundaries — never
    mid-sentence — so a fact is not separated from its anchor (e.g. a dining
    hall from its hours, or a numbered tip from its list).
"""
from __future__ import annotations

import re

CHUNK_SIZE = 800
OVERLAP = 120


def _sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences on ., !, ? followed by whitespace.

    Times like "1:00 am" and phone numbers like "413.597.2121" are not split
    because the period/colon is not followed by whitespace.
    """
    parts = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [p for p in parts if p]


def _segment(text: str, size: int) -> list[str]:
    """Break text into atomic units no larger than ``size``.

    Preference order: keep whole paragraphs; if a paragraph is too long, split
    into sentences; if a single sentence is still too long, hard-split on chars.
    """
    units: list[str] = []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    for para in paragraphs:
        if len(para) <= size:
            units.append(para)
            continue
        for sent in _sentences(para):
            if len(sent) <= size:
                units.append(sent)
            else:
                for i in range(0, len(sent), size):
                    units.append(sent[i : i + size])
    return units


def _overlap_units(units: list[str], overlap: int) -> list[str]:
    """Return the trailing units of a chunk totaling up to ``overlap`` chars."""
    tail: list[str] = []
    total = 0
    for u in reversed(units):
        if tail and total + len(u) > overlap:
            break
        tail.insert(0, u)
        total += len(u) + 1
    return tail


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Split a single document's text into overlapping, boundary-aware chunks."""
    units = _segment(text, size)
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    i = 0
    while i < len(units):
        u = units[i]
        sep = 1 if cur else 0
        if cur and cur_len + sep + len(u) > size:
            chunks.append("\n".join(cur).strip())
            cur = _overlap_units(cur, overlap) + [u]
            cur_len = sum(len(x) for x in cur) + max(0, len(cur) - 1)
        else:
            cur.append(u)
            cur_len += sep + len(u)
        i += 1
    if cur:
        tail = "\n".join(cur).strip()
        if tail:
            chunks.append(tail)
    return chunks


def chunk_documents(docs: list[dict], size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[dict]:
    """Chunk a list of ingested documents into a flat list of chunk records.

    Each record carries the metadata needed for retrieval and source attribution:
    ``{id, text, source, title, doc_id, chunk_index}``.
    """
    records: list[dict] = []
    for d in docs:
        for idx, piece in enumerate(chunk_text(d["text"], size, overlap)):
            records.append(
                {
                    "id": f"{d['doc_id']}::chunk{idx}",
                    "text": piece,
                    "source": d["source"],
                    "title": d["title"],
                    "doc_id": d["doc_id"],
                    "chunk_index": idx,
                }
            )
    return records
