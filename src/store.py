"""Stage 3 — Embedding + Vector Store.

Embeds chunk text with all-MiniLM-L6-v2 (sentence-transformers) and stores
vectors plus source metadata in a persistent ChromaDB collection.
The ChromaDB collection is written to ./chroma_db so build_index.py only
needs to run once; subsequent query.py runs just load the existing collection.
"""
from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "williams_guide"
CHROMA_DIR = "./chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH = 64  # embed this many chunks per call to keep memory flat


def _get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_DIR)


def build_store(chunks: list[dict]) -> chromadb.Collection:
    """Embed every chunk and upsert into a persistent ChromaDB collection.

    Metadata stored per chunk: source (URL), title, doc_id, chunk_index.
    Calling this function again with the same chunks is safe (upsert is idempotent).
    """
    model = SentenceTransformer(MODEL_NAME)
    client = _get_client()

    # delete + recreate so re-runs start fresh without duplicates
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "title": c["title"],
            "doc_id": c["doc_id"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    for start in range(0, len(texts), BATCH):
        end = min(start + BATCH, len(texts))
        batch_texts = texts[start:end]
        embeddings = model.encode(batch_texts, show_progress_bar=False).tolist()
        collection.add(
            ids=ids[start:end],
            documents=batch_texts,
            embeddings=embeddings,
            metadatas=metadatas[start:end],
        )
        print(f"  embedded chunks {start}–{end - 1}")

    print(f"Collection '{COLLECTION_NAME}' built: {collection.count()} chunks stored.")
    return collection


def load_store() -> chromadb.Collection:
    """Load the existing persistent collection (after build_index.py has run)."""
    client = _get_client()
    return client.get_collection(COLLECTION_NAME)
