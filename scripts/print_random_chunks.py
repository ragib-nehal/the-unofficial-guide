from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


from pipeline.config import PROJECT_ROOT

DEFAULT_CHUNKS_PATH = PROJECT_ROOT / "output" / "chunks.jsonl"


def load_chunks(path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def print_chunk(chunk: dict[str, Any], index: int) -> None:
    metadata = chunk.get("metadata", {})
    print("=" * 80)
    print(f"Random chunk {index}")
    print("=" * 80)
    print(f"chunk_id: {chunk.get('chunk_id')}")
    print(f"source_type: {metadata.get('source_type')}")
    print(f"source_file: {metadata.get('source_file')}")
    print(f"token_count: {chunk.get('token_count')}")

    professor_name = metadata.get("professor_name")
    course_number = metadata.get("course_number")
    if professor_name:
        print(f"professor_name: {professor_name}")
    if course_number:
        print(f"course_number: {course_number}")

    print("-" * 80)
    print(chunk.get("text", ""))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Print random chunks from chunks.jsonl.")
    parser.add_argument("--count", type=int, default=5, help="Number of random chunks to print.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducible samples.")
    parser.add_argument("--path", type=Path, default=DEFAULT_CHUNKS_PATH, help="Path to chunks.jsonl.")
    args = parser.parse_args()

    chunks = load_chunks(args.path)
    if not chunks:
        raise SystemExit(f"No chunks found in {args.path}")

    if args.seed is not None:
        random.seed(args.seed)

    sample_size = min(args.count, len(chunks))
    for index, chunk in enumerate(random.sample(chunks, sample_size), start=1):
        print_chunk(chunk, index)


if __name__ == "__main__":
    main()
