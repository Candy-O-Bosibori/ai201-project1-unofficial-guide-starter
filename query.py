"""End-to-end RAG query: retrieve → generate → return structured result.

``ask()`` is the single entry-point used by both the CLI and the Gradio UI.
"""
from __future__ import annotations

import sys
from src.retrieve import search
from src.generate import generate

TOP_K = 4


def ask(question: str, k: int = TOP_K) -> dict:
    """Retrieve top-k chunks for *question* and return a grounded answer.

    Return value:
        answer  – grounded model response with inline [Source N] citations
        sources – programmatic list of source titles (always present)
        chunks  – raw retrieved chunks (for UI display / evaluation)
    """
    chunks = search(question, k=k)
    return generate(question, chunks)


def _cli() -> None:
    if len(sys.argv) < 2:
        print("Usage: python query.py \"your question\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = ask(question)

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n" + "─" * 70)
    print("RETRIEVED FROM")
    print("─" * 70)
    for title in result["sources"]:
        print(f"  • {title}")

    print("\n" + "─" * 70)
    print("RETRIEVED CHUNKS (for inspection)")
    print("─" * 70)
    for i, chunk in enumerate(result["chunks"], 1):
        print(f"\n  [Source {i}] score={chunk['score']}  {chunk['doc_id']}")
        print("  " + chunk["text"][:300].replace("\n", "\n  ") + ("..." if len(chunk["text"]) > 300 else ""))


if __name__ == "__main__":
    _cli()
