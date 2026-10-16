# Project Chimera Intelligent Core

## Project Name
Project Chimera Document Intelligence System for Windows 11

## Objective
The primary objective of Project Chimera is to provide offline-capable, privacy-first semantic document question answering on Windows 11 workstations using local vector embeddings and low-latency LLM inference. It enables enterprise users to query proprietary technical manuals, legal reports, and research papers without leaking corporate data.

## Architecture
The system employs a 5-stage pipeline:
1. Ingestion: Format-specific text extraction supporting PDF, DOCX, TXT, CSV, and Markdown.
2. Chunking: Recursive character chunking with an 800-character window and 100-character sliding overlap.
3. Dense Embeddings: 384-dimensional dense semantic vectors generated locally via Sentence Transformers (all-MiniLM-L6-v2).
4. Vector Storage: Persistent ChromaDB collection utilizing HNSW cosine distance indexing.
5. Strict Prompt Generation: Context-injected LLM generation with strict truthfulness constraints.

## Technology Stack
- Backend: Python 3.11+, FastAPI, Uvicorn, python-dotenv
- Vector Store: ChromaDB (Local persistent storage)
- Embeddings: HuggingFace Sentence-Transformers (all-MiniLM-L6-v2)
- Frontend: React 18, Vite, Lucide Icons, Windows 11 Fluent CSS
- LLM Provider: Google Gemini API (gemini-2.5-flash)

## Advantages
- High privacy: Vector embeddings and similarity search execute 100% locally on the user machine.
- Sub-50ms retrieval: Local HNSW indexing provides near-instantaneous top-k semantic search.
- Native Windows 11 Design: Fluent UI aesthetic with live Retrieval Inspector for full RAG transparency.

## Limitations
- OCR dependency: Scanned image-only PDFs without text layers require pre-processing with OCR tools.
- Single-node: Designed for desktop workstations rather than multi-node distributed clusters.

## Future Scope
- Hybrid retrieval: Incorporating BM25 sparse lexical search alongside dense vector embeddings.
- Offline LLM fallback: Supporting local quantized models via Ollama or llama.cpp for fully air-gapped environments.
