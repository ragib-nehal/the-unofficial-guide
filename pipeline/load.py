from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pdfplumber

from .config import PDF_SOURCE, PipelinePaths, metadata_from_filename


@dataclass(frozen=True)
class Document:
    source_id: int
    source_type: str
    source_file: str
    url: str
    raw_text: str
    metadata: dict[str, str | int]


def load_documents(paths: PipelinePaths | None = None) -> list[Document]:
    paths = paths or PipelinePaths()
    documents = [_load_text_document(path) for path in sorted(paths.data_dir.glob("*.txt"))]

    pdf_path = paths.documents_dir / PDF_SOURCE["source_file"]
    if pdf_path.exists():
        documents.append(_load_pdf_document(pdf_path))

    return documents


def _load_text_document(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    url = lines[0].strip() if lines else ""
    raw_text = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
    metadata = metadata_from_filename(path.name)
    metadata["url"] = url

    return Document(
        source_id=int(metadata["source_id"]),
        source_type=str(metadata["source_type"]),
        source_file=path.name,
        url=url,
        raw_text=raw_text,
        metadata=metadata,
    )


def _load_pdf_document(path: Path) -> Document:
    page_texts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            if len(text) < 50:
                continue
            page_texts.append(f"PAGE {index}\n{text}")

    metadata = dict(PDF_SOURCE)
    metadata["page_count"] = len(page_texts)
    raw_text = "\n\n".join(page_texts).strip()
    return Document(
        source_id=int(PDF_SOURCE["source_id"]),
        source_type=str(PDF_SOURCE["source_type"]),
        source_file=str(PDF_SOURCE["source_file"]),
        url=str(PDF_SOURCE["url"]),
        raw_text=raw_text,
        metadata=metadata,
    )
