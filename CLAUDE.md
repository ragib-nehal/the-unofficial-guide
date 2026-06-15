# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"The Unofficial Guide" is a RAG (Retrieval-Augmented Generation) system that answers questions about CS courses and professors at Brooklyn College. It is a CodePath AI201 Week 1 project built in Python.

**Pipeline:** Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation

**Stack:**
- Embeddings: `all-MiniLM-L6-v2` via `sentence-transformers`
- Vector store: ChromaDB (local, stored in `chroma_db/` — gitignored)
- LLM: `llama-3.3-70b-versatile` via Groq API
- UI: Gradio or Streamlit (not yet decided; both are commented out in `requirements.txt`)

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GROQ_API_KEY` (free key at console.groq.com). ChromaDB runs fully locally — no other keys required.

## Data Layout

`data/` contains pre-scraped raw text files, each named `NN_sourcetype_identifier.txt`:
- `01–08`: Rate My Professors (one file per professor)
- `09–18`: Coursicle (one file per course)
- `19–21`: BC CIS Department HTML pages
- Source 22 (BC advising PDF) goes in `documents/` when added

**Chunking is source-type-specific:**

| Source | Strategy | Chunk size | Overlap |
|--------|----------|------------|---------|
| RMP (`rmp_`) | One review per chunk | ~100–200 tokens | ~20 tokens |
| Coursicle (`coursicle_`) | Section-based splits | 250 tokens | 25 tokens |
| PDF in `documents/` | Recursive splitting | 1000–1500 tokens | 150–250 tokens |

## Key Retrieval Parameters

- `top_k = 5` (cosine similarity search against ChromaDB)
- Chunk metadata must include: `source_type`, `professor_name` (RMP), `course_number` (Coursicle/BC)

## Planning Docs

- `planning.md` — full spec including eval questions, chunking rationale, and architecture diagram
- `README.md` — submission doc; fill it in section by section after each milestone

## Milestones Still Ahead

1. **Ingestion & chunking** — scraping scripts (BeautifulSoup for RMP/Coursicle/BC HTML, PyMuPDF for the advising PDF) + `chunk_documents()`
2. **Embedding & retrieval** — ChromaDB collection setup, `retrieve()` with logging
3. **Generation & UI** — Groq prompt template, Gradio/Streamlit interface
