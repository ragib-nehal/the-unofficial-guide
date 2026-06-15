from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed in the project env
    load_dotenv = None

try:
    from groq import Groq
except ImportError:  # pragma: no cover - dependency is installed in the project env
    Groq = None  # type: ignore[assignment]

if load_dotenv is not None:
    load_dotenv(override=True)

MODEL = "llama-3.3-70b-versatile"
DECLINE_PHRASE = "I don't have enough information on that."

SYSTEM_PROMPT = """You are a helpful Brooklyn College CS course and professor guide.

You are given documents containing student reviews, course information, and professor ratings from Brooklyn College.
Your job is to answer the user's question by summarizing what those documents say.

Rules:
- Base your answer on the provided documents. Do not add outside knowledge.
- Do not list or cite sources — the system handles that separately.
- If the documents contain relevant information, always answer using it. Even partial information is useful.
- Only respond with exactly "I don't have enough information on that." if the documents contain nothing relevant to the question.
- At Brooklyn College, CISC 3130 is the Data Structures course. Treat CISC3130 reviews as relevant to questions about Data Structures.
- Write in clear, concise prose."""

COURSE_ALIASES = {
    "data structures": "CISC3130",
    "data structure": "CISC3130",
    "modern programming techniques": "CISC3115",
    "advanced programming techniques": "CISC3110",
    "computer architecture": "CISC3310",
    "operating systems": "CISC3320",
    "artificial intelligence": "CISC3410",
    "machine learning": "CISC3440",
    "database systems": "CISC3810",
}


def format_source_label(chunk: dict[str, Any]) -> str:
    source_file = str(chunk.get("source_file", "unknown"))
    source_type = str(chunk.get("source_type", "unknown"))

    if source_type == "rmp":
        professor_name = chunk.get("professor_name") or _humanize_source_file(source_file)
        return f"{professor_name} reviews ({source_file})"

    if source_type == "coursicle":
        course_number = chunk.get("course_number") or _humanize_source_file(source_file)
        return f"{course_number} - Coursicle ({source_file})"

    return f"{_humanize_source_file(source_file)} ({source_file})"


def format_context(chunks: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = chunk.get("chunk_id", "unknown")
        source_type = chunk.get("source_type", "unknown")
        text = str(chunk.get("text", "")).strip()
        blocks.append(f"[Document {index} | {chunk_id} | {source_type}]\n{text}")
    return "\n\n".join(blocks)


def build_sources(chunks: list[dict[str, Any]]) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        label = format_source_label(chunk)
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return sources


def format_retrieved_chunks(chunks: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        label = format_source_label(chunk)
        text = str(chunk.get("text", "")).strip()
        match = chunk.get("match_type", "semantic")
        blocks.append(f"[{index}] {label} ({match})\n{text}")
    return "\n\n".join(blocks)


def select_context_chunks(
    chunks: list[dict[str, Any]], k: int = 5, question: str = ""
) -> list[dict[str, Any]]:
    semantic_chunks = [chunk for chunk in chunks if chunk.get("match_type", "semantic") == "semantic"]
    keyword_chunks = [chunk for chunk in chunks if chunk.get("match_type") == "keyword"]
    semantic_chunks = _rank_chunks_for_question(semantic_chunks, question)
    keyword_chunks = _rank_chunks_for_question(keyword_chunks, question)
    max_keyword_slots = 2 if k >= 5 else 1
    kw_take = min(len(keyword_chunks), max_keyword_slots)
    sem_take = k - kw_take
    selected = semantic_chunks[:sem_take] + keyword_chunks[:kw_take]
    if len(selected) < k:
        selected_ids = {id(chunk) for chunk in selected}
        leftovers = [chunk for chunk in semantic_chunks + keyword_chunks if id(chunk) not in selected_ids]
        selected.extend(leftovers[: k - len(selected)])
    return selected[:k]


def generate_answer(question: str, chunks: list[dict[str, Any]], client: Any | None = None) -> str:
    context_chunks = select_context_chunks(chunks, k=5, question=question)
    if not context_chunks:
        return DECLINE_PHRASE

    semantic = [
        chunk
        for chunk in context_chunks
        if chunk.get("match_type", "semantic") == "semantic" and chunk.get("distance") is not None
    ]
    if semantic and semantic[0]["distance"] > 0.75 and not _has_requested_grounding(context_chunks, question):
        return DECLINE_PHRASE

    client = client or _build_client()
    context = format_context(context_chunks)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def _build_client() -> Any:
    if Groq is None:
        raise RuntimeError("The groq package is required. Install dependencies with pip install -r requirements.txt.")
    return Groq(api_key=os.environ["GROQ_API_KEY"])


def _humanize_source_file(source_file: str) -> str:
    stem = Path(source_file).stem
    parts = stem.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    return " ".join(parts).upper() if parts[:2] == ["bc", "cs"] else " ".join(parts).title()


def _rank_chunks_for_question(chunks: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    professor_name = _requested_professor(question, chunks)
    course_number = _requested_course_number(question)

    def priority(item: tuple[int, dict[str, Any]]) -> tuple[int, int]:
        index, chunk = item
        score = 0
        if professor_name:
            if str(chunk.get("professor_name", "")).lower() == professor_name.lower():
                score -= 4
            elif chunk.get("professor_name"):
                score += 4
        if course_number and chunk.get("course_number") == course_number:
            score -= 2
        return score, index

    return [chunk for _, chunk in sorted(enumerate(chunks), key=priority)]


def _requested_professor(question: str, chunks: list[dict[str, Any]]) -> str:
    question_lower = question.lower()
    for chunk in chunks:
        professor_name = str(chunk.get("professor_name", ""))
        if professor_name and professor_name.lower() in question_lower:
            return professor_name
    return ""


def _requested_course_number(question: str) -> str:
    question_lower = question.lower()
    for phrase, course_number in COURSE_ALIASES.items():
        if phrase in question_lower:
            return course_number
    return ""


def _has_requested_grounding(chunks: list[dict[str, Any]], question: str) -> bool:
    professor_name = _requested_professor(question, chunks)
    course_number = _requested_course_number(question)
    if not professor_name or not course_number:
        return False
    return any(
        str(chunk.get("professor_name", "")).lower() == professor_name.lower()
        and chunk.get("course_number") == course_number
        for chunk in chunks
    )
