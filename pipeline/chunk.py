from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .clean import CleanedDocument
from .config import CHUNK_PARAMS
from .token_utils import count_tokens, split_by_tokens


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    token_count: int
    metadata: dict[str, str | int]


def chunk_documents(cleaned_documents: list[CleanedDocument]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in cleaned_documents:
        chunks.extend(chunk_document(document))
    return chunks


def chunk_document(document: CleanedDocument) -> list[Chunk]:
    if document.source_type == "rmp":
        texts = _chunk_rmp(document)
    elif document.source_type == "coursicle":
        texts = _chunk_labeled_sections(document, "coursicle")
    elif document.source_type == "bc_cis":
        texts = _chunk_bc(document)
    elif document.source_type == "pdf":
        texts = _chunk_pdf(document)
    else:
        params = CHUNK_PARAMS["bc_cis"]
        texts = split_by_tokens(document.text, params.size, params.overlap)

    chunks: list[Chunk] = []
    for index, text in enumerate(texts, start=1):
        metadata = dict(document.metadata)
        metadata["source_id"] = document.source_id
        metadata["source_type"] = document.source_type
        metadata["source_file"] = document.source_file
        metadata["url"] = document.url
        metadata["chunk_index"] = index

        course_number = _course_number_from_text(text)
        if course_number:
            metadata["course_number"] = course_number

        chunk_id = f"{Path(document.source_file).stem}_{index:03d}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                text=text.strip(),
                token_count=count_tokens(text),
                metadata=metadata,
            )
        )
    return chunks


def write_chunks_jsonl(chunks: list[Chunk], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(
                    {
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "token_count": chunk.token_count,
                        "metadata": chunk.metadata,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def _chunk_rmp(document: CleanedDocument) -> list[str]:
    params = CHUNK_PARAMS["rmp"]
    header = document.text.split("---", 1)[0].strip()
    blocks = [block.strip() for block in document.text.split("---")[1:] if block.strip()]
    chunks: list[str] = []
    for block in blocks:
        text = f"{header}\n{block}".strip()
        chunks.extend(split_by_tokens(text, params.size, params.overlap))
    return chunks


def _chunk_labeled_sections(document: CleanedDocument, source_type: str) -> list[str]:
    params = CHUNK_PARAMS[source_type]
    prefix = _section_prefix(document)
    sections = _split_substantive_sections(document.text)
    chunks: list[str] = []
    for section in sections:
        section_text = _ensure_prefix(prefix, section)
        chunks.extend(split_by_tokens(section_text, params.size, params.overlap))
    return chunks


def _chunk_bc(document: CleanedDocument) -> list[str]:
    text = document.text
    source_file = document.source_file
    if "courses_offered" in source_file:
        sections = _split_course_entries(text)
        params = CHUNK_PARAMS["bc_cis"]
        chunks: list[str] = []
        for section in sections:
            if count_tokens(section) <= 500:
                chunks.append(section)
            else:
                chunks.extend(split_by_tokens(section, params.size, params.overlap))
        return chunks
    if "major_requirements" in source_file:
        sections = _split_major_requirement_sections(text)
        params = CHUNK_PARAMS["bc_cis"]
        chunks = []
        for section in sections:
            chunks.extend(split_by_tokens(section, params.size, params.overlap))
        return chunks
    return _chunk_labeled_sections(document, "bc_cis")


def _chunk_pdf(document: CleanedDocument) -> list[str]:
    params = CHUNK_PARAMS["pdf"]
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", document.text) if paragraph.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        if current and current_tokens + paragraph_tokens > params.size:
            chunk_text = "\n\n".join(current).strip()
            chunks.append(chunk_text)
            overlap_text = _overlap_text(chunk_text, params.overlap)
            current = [overlap_text, paragraph] if overlap_text else [paragraph]
            current_tokens = count_tokens("\n\n".join(current))
            continue
        current.append(paragraph)
        current_tokens += paragraph_tokens
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks


def _split_substantive_sections(text: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^(REVIEWS:|DESCRIPTION:|METADATA:)", text))
    if not matches:
        return [text]
    sections: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.start() : end].strip()
        if section:
            sections.append(section)
    return sections


def _split_course_entries(text: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^\*?\d{4}[A-Z]?\b", text))
    if not matches:
        return [text]
    sections: list[str] = []
    preface = text[: matches[0].start()].strip()
    if preface:
        sections.append(preface)
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.start() : end].strip()
        if section:
            sections.append(section)
    return sections


def _split_major_requirement_sections(text: str) -> list[str]:
    headings = (
        "Computer Science Major Requirements",
        "Prerequisite Flowchart",
        "Possible Schedules",
        "Four Year Schedule",
        "Three Year Schedule",
        "Two-And-One-Half Year Schedule",
    )
    pattern = r"(?m)^(?=" + "|".join(re.escape(heading) for heading in headings) + r")"
    sections = [section.strip() for section in re.split(pattern, text) if section.strip()]
    return sections or [text]


def _section_prefix(document: CleanedDocument) -> str:
    if document.source_type == "coursicle":
        prefix_lines = []
        for line in document.text.splitlines():
            if line.startswith(("COURSE:", "TITLE:")):
                prefix_lines.append(line)
        return "\n".join(prefix_lines).strip()
    if document.source_type == "rmp":
        return f"PROFESSOR: {document.metadata.get('professor_name', '')}".strip()
    return ""


def _ensure_prefix(prefix: str, text: str) -> str:
    if not prefix or text.startswith(prefix):
        return text
    return f"{prefix}\n{text}".strip()


def _overlap_text(text: str, overlap: int) -> str:
    if count_tokens(text) <= overlap:
        return text
    return split_by_tokens(text, overlap, 0)[-1]


def _course_number_from_text(text: str) -> str:
    match = re.search(r"\bCISC\s*\d{4}[A-Z]?\b", text)
    if not match:
        return ""
    return match.group(0).replace(" ", "")
