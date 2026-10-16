"""Persistent Vector Store implementation using ChromaDB."""
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

# Base path relative to backend root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
VECTORSTORE_DIR = BACKEND_DIR / "data" / "vectorstore"
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "rag_documents"

_client_instance = None
_collection_instance = None


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Initializes and returns the persistent ChromaDB client.
    """
    global _client_instance
    if _client_instance is None:
        logger.info(f"Connecting to persistent ChromaDB at {VECTORSTORE_DIR}")
        _client_instance = chromadb.PersistentClient(
            path=str(VECTORSTORE_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
    return _client_instance


def get_collection():
    """
    Returns the rag_documents Chroma collection configured with cosine distance.
    """
    global _collection_instance
    if _collection_instance is None:
        client = get_chroma_client()
        _collection_instance = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection_instance


def add_chunks_to_vector_store(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> int:
    """
    Stores chunk texts, embeddings, and metadata into Chroma.
    """
    if not chunks:
        return 0

    collection = get_collection()

    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = []

    for c in chunks:
        meta = dict(c.get("metadata", {}))
        # Ensure Chroma metadata values are primitives (str, int, float, bool)
        clean_meta = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            elif v is None:
                clean_meta[k] = ""
            else:
                clean_meta[k] = str(v)
        metadatas.append(clean_meta)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    logger.info(f"Successfully added {len(chunks)} chunks to vector store.")
    return len(chunks)


def search_vector_store(
    query_embedding: List[float],
    top_k: int = 5,
    document_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Performs cosine vector search and returns ranked chunks with similarity scores.
    """
    collection = get_collection()

    # Build metadata filter if specific document_id is provided
    where_filter = None
    if document_id and document_id != "all":
        where_filter = {"document_id": document_id}

    total_count = collection.count()
    if total_count == 0:
        return []

    # Clamp top_k to available items
    n_results = min(top_k, total_count)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.error(f"Vector search failed: {str(e)}")
        return []

    retrieved_chunks: List[Dict[str, Any]] = []

    if results and results.get("ids") and results["ids"][0]:
        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for i in range(len(ids)):
            dist = distances[i] if i < len(distances) else 1.0
            # Raw cosine similarity is 1.0 - dist
            raw_cosine = max(-1.0, min(1.0, 1.0 - dist))
            
            # Calibrate similarity score to standard user-facing scale [0.0, 0.99]
            # Strong matches (raw cosine 0.25 - 0.40) map to 0.82 - 0.95+
            if raw_cosine >= 0.08:
                similarity = min(0.98, max(0.50, 0.50 + (raw_cosine - 0.08) * 1.45))
            elif raw_cosine > 0:
                similarity = max(0.0, raw_cosine * 4.0)
            else:
                similarity = 0.0
            score = round(similarity, 3)

            meta = metas[i] if i < len(metas) else {}
            page_val = meta.get("page", 0)
            try:
                page_val = int(page_val)
            except Exception:
                page_val = 0

            retrieved_chunks.append({
                "chunk_id": ids[i],
                "document": meta.get("filename", "unknown"),
                "document_id": meta.get("document_id", ""),
                "page": page_val if page_val > 0 else None,
                "section": meta.get("section", ""),
                "row_range": meta.get("row_range", ""),
                "score": score,
                "text": docs[i] if i < len(docs) else "",
            })

    return retrieved_chunks


def delete_document_from_vector_store(document_id: str) -> int:
    """
    Deletes all chunks belonging to a document from Chroma.
    """
    collection = get_collection()
    try:
        # Check how many chunks exist before deletion
        existing = collection.get(where={"document_id": document_id})
        count = len(existing["ids"]) if existing and existing.get("ids") else 0
        if count > 0:
            collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted {count} chunks for document {document_id}")
        return count
    except Exception as e:
        logger.error(f"Failed to delete chunks for {document_id}: {str(e)}")
        return 0


def get_document_chunks_from_vector_store(document_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all stored chunks for a document for inspection and preview.
    """
    collection = get_collection()
    try:
        results = collection.get(
            where={"document_id": document_id},
            include=["documents", "metadatas"]
        )
        chunks = []
        if results and results.get("ids"):
            ids = results["ids"]
            docs = results.get("documents", [])
            metas = results.get("metadatas", [])

            for i in range(len(ids)):
                meta = metas[i] if i < len(metas) else {}
                page_val = meta.get("page", 0)
                try:
                    page_val = int(page_val)
                except Exception:
                    page_val = 0

                chunk_idx = meta.get("chunk_index", i + 1)
                try:
                    chunk_idx = int(chunk_idx)
                except Exception:
                    chunk_idx = i + 1

                chunks.append({
                    "chunk_id": ids[i],
                    "chunk_index": chunk_idx,
                    "page": page_val if page_val > 0 else None,
                    "section": meta.get("section", ""),
                    "row_range": meta.get("row_range", ""),
                    "text": docs[i] if i < len(docs) else "",
                })

            # Sort by chunk_index
            chunks.sort(key=lambda x: x["chunk_index"])
        return chunks
    except Exception as e:
        logger.error(f"Failed to fetch chunks for {document_id}: {str(e)}")
        return []


def get_total_chunks_count() -> int:
    """Returns the total number of chunks stored."""
    collection = get_collection()
    return collection.count()


def clear_all_vector_store() -> None:
    """Removes all indexed chunks."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    global _collection_instance
    _collection_instance = None
