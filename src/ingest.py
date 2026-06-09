"""Stage 1 — Document ingestion.

Loads the cleaned .txt files from ``documents/``, parses the source/title header
that was written at collection time into metadata, and returns structured records
ready for chunking. The documents are already cleaned (navigation/ads/boilerplate
were stripped when collected), so ``clean_text`` only normalizes whitespace so that
chunk boundaries are predictable — it does not re-clean already-clean text.
"""
from __future__ import annotations

import re
from pathlib import Path

HEADER_SEP = "---"


def clean_text(text: str) -> str:
    """Normalize whitespace on already-clean document text.

    - unify line endings
    - strip trailing spaces on each line
    - collapse 3+ consecutive newlines into a single blank line
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _parse(raw: str) -> tuple[dict, str]:
    """Split a raw file into (metadata, body).

    The header is the block of ``KEY: value`` lines before the first line that is
    exactly ``---``. If no header is present, the whole file is treated as body.
    """
    lines = raw.split("\n")
    meta: dict[str, str] = {}
    body_start = 0
    if any(line.strip() == HEADER_SEP for line in lines[:12]):
        for i, line in enumerate(lines):
            if line.strip() == HEADER_SEP:
                body_start = i + 1
                break
            m = re.match(r"([A-Za-z_]+):\s*(.*)", line)
            if m:
                meta[m.group(1).lower()] = m.group(2).strip()
    body = "\n".join(lines[body_start:])
    return meta, body


def load_documents(directory: str = "documents") -> list[dict]:
    """Load and clean every .txt document in ``directory``.

    Returns a list of dicts: ``{doc_id, source, title, type, text}``.
    """
    docs: list[dict] = []
    for path in sorted(Path(directory).glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        meta, body = _parse(raw)
        docs.append(
            {
                "doc_id": path.stem,
                "source": meta.get("source_url", ""),
                "title": meta.get("title", path.stem),
                "type": meta.get("type", ""),
                "text": clean_text(body),
            }
        )
    return docs


if __name__ == "__main__":
    loaded = load_documents("documents")
    print(f"Loaded {len(loaded)} documents:")
    for d in loaded:
        print(f"  {d['doc_id']:<40} {len(d['text']):>6} chars  [{d['type']}]  {d['title']}")
