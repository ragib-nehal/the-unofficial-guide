from __future__ import annotations

from typing import Any

from pipeline.generate import build_sources, format_retrieved_chunks, generate_answer, select_context_chunks

retrieve = None


def ask(question: str, k: int = 5) -> dict[str, Any]:
    retrieve_fn = retrieve or _load_retrieve()
    chunks = retrieve_fn(question, k=k, hybrid=True)
    context_chunks = select_context_chunks(chunks, k=k, question=question)
    answer = generate_answer(question, chunks)
    return {
        "answer": answer,
        "sources": build_sources(context_chunks),
        "chunks": format_retrieved_chunks(context_chunks),
    }


def _load_retrieve():
    from pipeline.retrieve import retrieve as retrieve_fn

    return retrieve_fn
