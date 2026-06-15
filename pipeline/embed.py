from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import chromadb
from chromadb import Collection
from sentence_transformers import SentenceTransformer

from .config import PipelinePaths

COLLECTION_NAME = "unofficial_guide"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64


def load_chunks(path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def get_collection(client: chromadb.PersistentClient, name: str, rebuild: bool) -> Collection:
    if rebuild:
        try:
            client.delete_collection(name)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def build_vector_store(chunks: list[dict[str, Any]], collection: Collection) -> None:
    model = SentenceTransformer(MODEL_NAME)
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        ids = [chunk["chunk_id"] for chunk in batch]
        texts = [chunk["text"] for chunk in batch]
        metadatas = [_sanitize_metadata(chunk["metadata"]) for chunk in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        print(f"  Embedded {start + len(batch)}/{len(chunks)} chunks")


def embed_all(paths: PipelinePaths | None = None, rebuild: bool = False) -> Collection:
    paths = paths or PipelinePaths()
    chunks = load_chunks(paths.chunks_path)
    print(f"Loaded {len(chunks)} chunks from {paths.chunks_path}")

    chroma_path = paths.root / "chroma_db"
    client = chromadb.PersistentClient(path=str(chroma_path))
    collection = get_collection(client, COLLECTION_NAME, rebuild)

    existing = collection.count()
    if existing > 0 and not rebuild:
        print(f"Collection already has {existing} vectors — skipping. Use --rebuild to re-embed.")
        return collection

    build_vector_store(chunks, collection)
    print(f"Stored {collection.count()} vectors in {chroma_path}")
    return collection


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    sanitized: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        else:
            sanitized[key] = str(value)
    return sanitized
