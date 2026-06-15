from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ChunkParams:
    size: int
    overlap: int


@dataclass(frozen=True)
class PipelinePaths:
    root: Path = PROJECT_ROOT
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "raw")
    documents_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "documents")
    cleaned_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "cleaned")
    output_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "output")

    @property
    def chunks_path(self) -> Path:
        return self.output_dir / "chunks.jsonl"


CHUNK_PARAMS = {
    "rmp": ChunkParams(size=200, overlap=20),
    "coursicle": ChunkParams(size=250, overlap=25),
    "bc_cis": ChunkParams(size=250, overlap=25),
    "pdf": ChunkParams(size=1250, overlap=200),
}

PDF_SOURCE = {
    "source_id": 22,
    "source_type": "pdf",
    "source_file": "codepat.pdf",
    "url": "https://www.sci.brooklyn.cuny.edu/~cis/UndergradJava2022.pdf",
    "title": "BC CS Undergrad Advising Guide (Java Track, 2022)",
}


def infer_source_type(filename: str) -> str:
    stem = Path(filename).stem
    if "_rmp_" in f"_{stem}_":
        return "rmp"
    if "_coursicle_" in f"_{stem}_":
        return "coursicle"
    if "_bc_cis_" in f"_{stem}_" or "_bc_cs_" in f"_{stem}_":
        return "bc_cis"
    raise ValueError(f"Cannot infer source type from filename: {filename}")


def source_id_from_filename(filename: str) -> int:
    prefix = Path(filename).name.split("_", 1)[0]
    if not prefix.isdigit():
        raise ValueError(f"Expected numeric filename prefix: {filename}")
    return int(prefix)


def identifier_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    return stem.split("_", 2)[2]


def title_case_identifier(identifier: str) -> str:
    return " ".join(part.capitalize() for part in identifier.split("_"))


def course_number_from_identifier(identifier: str) -> str:
    parts = identifier.split("_")
    if len(parts) >= 2 and parts[0].lower() == "cisc":
        return f"CISC {parts[1].upper()}"
    return identifier.upper()


def metadata_from_filename(filename: str) -> dict[str, str | int]:
    source_type = infer_source_type(filename)
    identifier = identifier_from_filename(filename)
    metadata: dict[str, str | int] = {
        "source_id": source_id_from_filename(filename),
        "source_type": source_type,
        "source_file": Path(filename).name,
        "identifier": identifier,
    }
    if source_type == "rmp":
        metadata["professor_name"] = title_case_identifier(identifier)
    elif source_type == "coursicle":
        metadata["course_number"] = course_number_from_identifier(identifier)
    return metadata
