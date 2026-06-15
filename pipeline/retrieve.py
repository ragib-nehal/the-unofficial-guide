from __future__ import annotations

import re
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from .config import PipelinePaths
from .embed import COLLECTION_NAME, MODEL_NAME

_STOPWORDS = {
    "what", "the", "is", "are", "for", "a", "an", "in", "of",
    "or", "and", "do", "does", "how", "which", "that", "this",
    "to", "about", "with", "have", "i", "at", "from", "can", "be",
    "course", "courses", "student", "students",
}


def retrieve(
    query: str,
    k: int = 5,
    collection: chromadb.Collection | None = None,
    hybrid: bool = True,
) -> list[dict[str, Any]]:
    if collection is None:
        paths = PipelinePaths()
        client = chromadb.PersistentClient(path=str(paths.root / "chroma_db"))
        collection = client.get_collection(COLLECTION_NAME)

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks: list[dict[str, Any]] = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (chunk_id, text, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances), start=1
    ):
        source_type = metadata.get("source_type", "unknown")
        source_file = metadata.get("source_file", "unknown")
        print(f"[{rank}] {chunk_id} | {source_type} | distance: {distance:.3f} | {source_file}")
        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "distance": distance,
                "match_type": "semantic",
                **metadata,
            }
        )

    if hybrid:
        keywords = _extract_keywords(query)
        kw_chunks = _keyword_fetch(collection, keywords, {c["chunk_id"] for c in chunks}, limit=k)
        for rank, chunk in enumerate(kw_chunks, start=len(chunks) + 1):
            print(
                f"[{rank}] {chunk['chunk_id']} | {chunk.get('source_type', 'unknown')} "
                f"| keyword | {chunk.get('source_file', 'unknown')}"
            )
        chunks.extend(kw_chunks)

    return chunks


def _extract_keywords(query: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z]+", query.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) >= 4]


def _keyword_fetch(
    collection: chromadb.Collection,
    keywords: list[str],
    exclude_ids: set[str],
    limit: int = 5,
) -> list[dict[str, Any]]:
    seen: set[str] = set(exclude_ids)
    results: list[dict[str, Any]] = []
    for kw in keywords:
        try:
            fetched = collection.get(
                where_document={"$contains": kw},
                include=["documents", "metadatas"],
            )
        except Exception:
            continue
        for chunk_id, text, metadata in zip(
            fetched["ids"], fetched["documents"], fetched["metadatas"]
        ):
            if chunk_id not in seen:
                seen.add(chunk_id)
                results.append(
                    {
                        "chunk_id": chunk_id,
                        "text": text,
                        "distance": None,
                        "match_type": "keyword",
                        **metadata,
                    }
                )
            if len(results) >= limit:
                return results
    return results
