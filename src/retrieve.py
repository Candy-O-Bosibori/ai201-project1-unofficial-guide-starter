"""Stage 4 — Retrieval.

Embeds a user query with the same all-MiniLM-L6-v2 model and performs
semantic similarity search against the ChromaDB collection.
Returns the top-k chunks with text, score, and source metadata.
"""
from __future__ import annotations

from sentence_transformers import SentenceTransformer

from src.store import load_store, MODEL_NAME

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def search(query: str, k: int = 4) -> list[dict]:
    """Return the top-k most semantically relevant chunks for *query*.

    Each result is a dict:
        text        – the chunk text
        source      – original URL
        title       – document title
        doc_id      – file stem (e.g. '02-dining-services')
        chunk_index – position within its document
        score       – cosine distance (lower = more similar; 0 is identical)
    """
    collection = load_store()
    model = _get_model()
    embedding = model.encode(query, show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits: list[dict] = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append(
            {
                "text": text,
                "source": meta.get("source", ""),
                "title": meta.get("title", ""),
                "doc_id": meta.get("doc_id", ""),
                "chunk_index": meta.get("chunk_index", -1),
                "score": round(dist, 4),
            }
        )
    return hits
