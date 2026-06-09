"""Phase 3 retrieval test — run 3 eval questions, print chunks + scores."""
from src.retrieve import search

QUERIES = [
    ("Q1", "Which dining hall is open the latest at night, and until what time?"),
    ("Q2", "What is Mountain Day at Williams and what do students do?"),
    ("Q3", "What's the best time to do laundry in the dorms, according to students?"),
]

for label, q in QUERIES:
    print("\n" + "=" * 72)
    print(f"{label}: {q}")
    print("=" * 72)
    hits = search(q, k=4)
    for i, h in enumerate(hits, 1):
        print(f"\n  [{i}] score={h['score']}  |  {h['doc_id']}  (chunk {h['chunk_index']})")
        print(f"      Title: {h['title']}")
        print("      ---")
        print("      " + h["text"][:500].replace("\n", "\n      "))
        if len(h["text"]) > 500:
            print("      [...]")
