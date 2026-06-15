import gradio as gr

from query import ask


def handle_query(question: str):
    if not question.strip():
        return "Enter a question about Brooklyn College CS courses or professors.", "", ""
    result = ask(question)
    sources = "\n".join(f"- {source}" for source in result["sources"])
    return result["answer"], sources, result["chunks"]


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown("# The Unofficial Guide\nAsk about Brooklyn College CS courses and professors.")
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about Moshe Lach for Data Structures?",
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    chunks = gr.Textbox(label="Retrieved chunks", lines=12)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources, chunks])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, chunks])


if __name__ == "__main__":
    demo.launch()
