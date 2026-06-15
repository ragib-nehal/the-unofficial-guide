from __future__ import annotations

import re

import tiktoken


ENCODING = None


def _encoding():
    global ENCODING
    if ENCODING is None:
        ENCODING = tiktoken.get_encoding("cl100k_base")
    return ENCODING


def count_tokens(text: str) -> int:
    try:
        return len(_encoding().encode(text))
    except Exception:
        return len(_fallback_tokens(text))


def split_by_tokens(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("Overlap must be non-negative and smaller than chunk size")

    try:
        tokens = _encoding().encode(text)
        decode = _encoding().decode
    except Exception:
        tokens = _fallback_tokens(text)
        decode = _decode_fallback

    if len(tokens) <= size:
        return [text.strip()] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        chunk = decode(tokens[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
        start = end - overlap
    return chunks


def _fallback_tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


def _decode_fallback(tokens: list[str]) -> str:
    text = " ".join(tokens)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text
