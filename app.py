"""Gradio web UI for the Williams College Unofficial Guide RAG system.

Run:  python app.py
Then open http://localhost:7860 in a browser.
"""
import gradio as gr
from query import ask


def _retrieval_quality(best_score: float) -> str:
    """Single overall retrieval quality label based on the top chunk's cosine distance."""
    if best_score <= 0.45:
        return f"✅  Strong match  (score {best_score:.3f})"
    if best_score <= 0.57:
        return f"⚠️  Fair match  (score {best_score:.3f}) — answer may be partial"
    return f"❌  Weak match  (score {best_score:.3f}) — topic may not be in the documents"


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", "", ""

    result = ask(question)

    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    best_score = result["chunks"][0]["score"]
    quality_text = _retrieval_quality(best_score)

    chunks_text = ""
    for i, chunk in enumerate(result["chunks"], 1):
        chunks_text += (
            f"[Source {i}] score={chunk['score']}  |  {chunk['doc_id']}\n"
            f"{chunk['text'][:400]}{'...' if len(chunk['text']) > 400 else ''}\n\n"
        )

    return result["answer"], sources_text, quality_text, chunks_text.strip()


with gr.Blocks(title="Williams College Unofficial Guide") as demo:
    gr.Markdown(
        "## Williams College Unofficial Guide\n"
        "Ask anything about campus life — dining, dorms, traditions, weather, "
        "orientation, and more. Answers are grounded strictly in collected student "
        "documents; sources are always shown."
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder='e.g. "Which dining hall is open the latest?"',
            scale=5,
        )
        btn = gr.Button("Ask", variant="primary", scale=1)

    answer_box = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources_box = gr.Textbox(label="Retrieved from", lines=4, interactive=False)
    scores_box = gr.Textbox(
        label="Retrieval quality",
        lines=1,
        interactive=False,
    )

    with gr.Accordion("Retrieved chunks (full text)", open=False):
        chunks_box = gr.Textbox(label="", lines=12, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box, scores_box, chunks_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box, scores_box, chunks_box])

    gr.Examples(
        examples=[
            ["What is Mountain Day at Williams and what do students do?"],
            ["What should I expect from spring weather in Williamstown?"],
            ["What's the best time to do laundry in the dorms?"],
            ["Which dining hall is open the latest at night, and until what time?"],
            ["Where can I park my car on campus?"],
        ],
        inputs=inp,
    )


if __name__ == "__main__":
    demo.launch()
