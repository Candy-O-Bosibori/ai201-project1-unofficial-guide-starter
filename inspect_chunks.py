"""Phase 2 inspection — run ingestion + chunking, print 5 representative chunks,
and report the total chunk count against the 50-2000 sanity range.

Usage:  python inspect_chunks.py
"""
from collections import Counter

from src.ingest import load_documents
from src.chunk import chunk_documents, CHUNK_SIZE, OVERLAP


def main() -> None:
    docs = load_documents("documents")
    print(f"Loaded {len(docs)} documents from documents/")

    chunks = chunk_documents(docs)
    total = len(chunks)

    # Pick 5 chunks evenly spread across the whole corpus so the sample is
    # representative (different documents, not just the first one).
    if total >= 5:
        idxs = sorted({round(i * (total - 1) / 4) for i in range(5)})
    else:
        idxs = list(range(total))

    print("\n" + "=" * 72)
    print("5 REPRESENTATIVE CHUNKS")
    print("=" * 72)
    for j in idxs:
        c = chunks[j]
        print(f"\n--- chunk #{j}  [{c['title']}]  ({len(c['text'])} chars) ---")
        print(c["text"])

    sizes = [len(c["text"]) for c in chunks]
    print("\n" + "=" * 72)
    print("STATS")
    print("=" * 72)
    print(f"chunk size target = {CHUNK_SIZE}, overlap = {OVERLAP}")
    print(f"TOTAL CHUNKS: {total}")
    print(f"avg chars/chunk: {sum(sizes) // total}   min: {min(sizes)}   max: {max(sizes)}")

    per = Counter(c["doc_id"] for c in chunks)
    print("\nchunks per document:")
    for d in docs:
        print(f"  {d['doc_id']:<40} {per[d['doc_id']]:>3}")

    print()
    if total < 50:
        print(f"[!] {total} < 50 — chunks may be too large for precise matching.")
    elif total > 2000:
        print(f"[!] {total} > 2000 — chunks may be too small.")
    else:
        print(f"[OK] {total} chunks is within the recommended 50-2000 range.")


if __name__ == "__main__":
    main()
