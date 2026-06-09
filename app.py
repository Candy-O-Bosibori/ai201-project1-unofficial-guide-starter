"""Gradio web UI for the Williams College Unofficial Guide RAG system.

Run:  python app.py
Then open http://localhost:7860 in a browser.
"""
import gradio as gr
from query import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", ""

    result = ask(question)

    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    chunks_text = ""
    for i, chunk in enumerate(result["chunks"], 1):
        chunks_text += (
            f"[Source {i}] score={chunk['score']}  |  {chunk['doc_id']}\n"
            f"{chunk['text'][:400]}{'...' if len(chunk['text']) > 400 else ''}\n\n"
        )

    return result["answer"], sources_text, chunks_text.strip()


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

    with gr.Accordion("Retrieved chunks (for inspection)", open=False):
        chunks_box = gr.Textbox(label="", lines=12, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box, chunks_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box, chunks_box])

    gr.Examples(
        examples=[
            ["Which dining hall is open the latest at night, and until what time?"],
            ["What is Mountain Day at Williams and what do students do?"],
            ["What's the best time to do laundry in the dorms?"],
            ["What should I expect from spring weather in Williamstown?"],
            ["What is Williams' policy on hard alcohol and large parties?"],
        ],
        inputs=inp,
    )


if __name__ == "__main__":
    demo.launch()
