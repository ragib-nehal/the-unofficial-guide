from __future__ import annotations

import argparse
from collections import Counter

from .chunk import Chunk, chunk_documents, write_chunks_jsonl
from .clean import CleanedDocument, clean_documents, write_cleaned_documents
from .config import PipelinePaths
from .load import load_documents


REPRESENTATIVE_KEYS = (
    ("rmp", None),
    ("coursicle", None),
    ("bc_cis", "courses_offered"),
    ("bc_cis", "major_requirements"),
    ("pdf", None),
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load, clean, and chunk project documents.")
    parser.add_argument("--clean-only", action="store_true", help="Print one cleaned sample per source type.")
    parser.add_argument("--inspect", action="store_true", help="Print representative chunks and chunk counts.")
    args = parser.parse_args()

    paths = PipelinePaths()
    documents = load_documents(paths)
    cleaned_documents = clean_documents(documents)
    write_cleaned_documents(cleaned_documents, paths)

    print(f"Loaded {len(documents)} documents")
    print(f"Wrote cleaned documents to {paths.cleaned_dir}")

    if args.clean_only:
        print_clean_samples(cleaned_documents)
        return

    chunks = chunk_documents(cleaned_documents)
    write_chunks_jsonl(chunks, paths.chunks_path)
    print(f"Wrote {len(chunks)} chunks to {paths.chunks_path}")

    if args.inspect:
        print_chunk_inspection(chunks)


def print_clean_samples(cleaned_documents: list[CleanedDocument]) -> None:
    seen: set[str] = set()
    for document in cleaned_documents:
        if document.source_type in seen:
            continue
        seen.add(document.source_type)
        print("\n" + "=" * 80)
        print(f"CLEAN SAMPLE: {document.source_type} | {document.source_file}")
        print("=" * 80)
        print(document.text)


def print_chunk_inspection(chunks: list[Chunk]) -> None:
    print("\n" + "=" * 80)
    print("CHUNK INSPECTION")
    print("=" * 80)
    for chunk in representative_chunks(chunks):
        print(f"\n{chunk.chunk_id} | {chunk.metadata.get('source_type')} | {chunk.token_count} tokens")
        print("-" * 80)
        print(chunk.text[:1000])

    counts = Counter(str(chunk.metadata.get("source_type", "unknown")) for chunk in chunks)
    print("\n" + "=" * 80)
    print("CHUNK COUNTS")
    print("=" * 80)
    print(f"Total chunks: {len(chunks)}")
    for source_type, count in sorted(counts.items()):
        print(f"{source_type}: {count}")
    if len(chunks) < 50:
        print("WARNING: Fewer than 50 chunks; chunks may be too large.")
    elif len(chunks) > 2000:
        print("WARNING: More than 2,000 chunks; chunks may be too small.")
    else:
        print("Chunk count is within the 50-2,000 milestone sanity range.")


def representative_chunks(chunks: list[Chunk]) -> list[Chunk]:
    selected: list[Chunk] = []
    used_ids: set[str] = set()
    for source_type, filename_hint in REPRESENTATIVE_KEYS:
        for chunk in chunks:
            if chunk.chunk_id in used_ids:
                continue
            if chunk.metadata.get("source_type") != source_type:
                continue
            if filename_hint and filename_hint not in str(chunk.metadata.get("source_file", "")):
                continue
            selected.append(chunk)
            used_ids.add(chunk.chunk_id)
            break
    return selected[:5]


if __name__ == "__main__":
    main()
