"""Retrieval service for vector similarity query and context compilation."""
import os
import logging
from typing import List, Dict, Any, Optional

from .embeddings import embed_text
from .vector_store import search_vector_store

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = int(os.getenv("TOP_K", "5"))


def retrieve_relevant_chunks(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    document_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Executes semantic vector retrieval:
    1. Embeds question using SentenceTransformer.
    2. Performs vector similarity search in ChromaDB.
    3. Returns top-k matching chunks with similarity scores.
    """
    if not question or not question.strip():
        return []

    # 1. Embed query
    logger.info(f"Generating embedding for question: '{question[:60]}...'")
    query_vector = embed_text(question.strip())

    # 2. Search Chroma vector store
    logger.info(f"Querying vector store (top_k={top_k}, document_id={document_id})")
    chunks = search_vector_store(
        query_embedding=query_vector,
        top_k=top_k,
        document_id=document_id
    )

    return chunks


def build_context_from_sources(sources: List[Dict[str, Any]]) -> str:
    """
    Builds a clean, structured context string from retrieved chunks to feed the LLM.
    """
    if not sources:
        return "No relevant context found."

    context_segments = []
    for i, s in enumerate(sources, start=1):
        doc_name = s.get("document", "Unknown")
        page = s.get("page")
        section = s.get("section")
        score = s.get("score", 0.0)
        chunk_id = s.get("chunk_id", f"chunk_{i}")
        text = s.get("text", "").strip()

        loc_parts = [f"Document: {doc_name}"]
        if page:
            loc_parts.append(f"Page: {page}")
        if section:
            loc_parts.append(f"Section: {section}")
        loc_parts.append(f"Chunk ID: {chunk_id}")
        loc_parts.append(f"Similarity Score: {score}")

        header = f"[Source {i} | " + " | ".join(loc_parts) + "]"
        context_segments.append(f"{header}\n{text}")

    return "\n\n--------------------\n\n".join(context_segments)
