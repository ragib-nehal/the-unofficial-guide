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
    "course", "courses", "student", "students", "data", "structures",
}

PROFESSOR_NAMES = (
    "Moshe Lach",
    "Basak Taylan",
    "Gabriel Yarmish",
    "Noson Yanofsky",
    "Kleanthis Psarris",
    "Hui Chen",
    "Matthew Mcneill",
    "Robert Zwick",
)

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
    query_lower = query.lower()
    keywords: list[str] = []

    for name in PROFESSOR_NAMES:
        if name.lower() in query_lower:
            keywords.append(name)

    for phrase, course_number in COURSE_ALIASES.items():
        if phrase in query_lower:
            keywords.append(course_number)

    for course_number in re.findall(r"\b(?:CISC\s*)?(\d{4}[A-Z]?)\b", query, flags=re.IGNORECASE):
        keywords.append(f"CISC{course_number.upper()}")

    alpha_tokens = re.findall(r"[a-zA-Z]+", query)
    alpha_kws = [
        token if token[:1].isupper() else token.lower()
        for token in alpha_tokens
        if token.lower() not in _STOPWORDS and len(token) >= 4
    ]
    keywords.extend(alpha_kws)
    return list(dict.fromkeys(keywords))


def _keyword_fetch(
    collection: chromadb.Collection,
    keywords: list[str],
    exclude_ids: set[str],
    limit: int = 5,
) -> list[dict[str, Any]]:
    seen: set[str] = set(exclude_ids)
    results: list[dict[str, Any]] = []
    for kw in keywords:
        fetched = _fetch_keyword(collection, kw)
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


def _fetch_keyword(collection: chromadb.Collection, keyword: str) -> dict[str, list[Any]]:
    if " " in keyword:
        return _safe_get(collection, where={"professor_name": keyword})
    if re.fullmatch(r"(?:CISC)?\d{4}[A-Z]?", keyword, flags=re.IGNORECASE):
        course_number = keyword.upper() if keyword.upper().startswith("CISC") else f"CISC{keyword}"
        return _safe_get(collection, where={"course_number": course_number})

    fetched = _safe_get(collection, where_document={"$contains": keyword})
    if not fetched["ids"] and keyword.islower():
        return _safe_get(collection, where_document={"$contains": keyword.title()})
    return fetched


def _safe_get(collection: chromadb.Collection, **kwargs: Any) -> dict[str, list[Any]]:
    try:
        return collection.get(include=["documents", "metadatas"], **kwargs)
    except Exception:
        return {"ids": [], "documents": [], "metadatas": []}
