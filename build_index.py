"""One-shot script: ingest → chunk → embed → persist to ./chroma_db.

Run once before using query.py. Safe to re-run — it recreates the collection.

Usage: python build_index.py
"""
from src.ingest import load_documents
from src.chunk import chunk_documents
from src.store import build_store


def main() -> None:
    print("=== Stage 1: Loading documents ===")
    docs = load_documents("documents")
    print(f"Loaded {len(docs)} documents.")

    print("\n=== Stage 2: Chunking ===")
    chunks = chunk_documents(docs)
    print(f"Produced {len(chunks)} chunks.")

    print("\n=== Stage 3: Embedding + storing in ChromaDB ===")
    build_store(chunks)
    print("\nIndex built. Run  python query.py \"your question\"  to query.")


if __name__ == "__main__":
    main()
