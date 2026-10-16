"""Document management and processing routes."""
import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from ..services.loaders import load_document
from ..services.chunking import create_chunks_for_document
from ..services.document_store import (
    list_documents,
    get_document,
    add_document,
    remove_document,
)
from ..embeddings import embed_batch
from ..vector_store import (
    add_chunks_to_vector_store,
    delete_document_from_vector_store,
    get_document_chunks_from_vector_store,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Documents"])

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BACKEND_DIR / "data" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".md", ".markdown"}


def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    RAG Document Ingestion Pipeline:
    1. Validate file extension and size
    2. Save document locally to backend/data/uploads/
    3. Extract text sections / pages
    4. Clean & split text into configurable chunks
    5. Generate embeddings using SentenceTransformers
    6. Store vectors & metadata in persistent ChromaDB
    7. Save document metadata
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided or missing filename.")

    original_filename = file.filename
    ext = Path(original_filename).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}_{original_filename}"
    saved_path = UPLOADS_DIR / safe_filename

    # Read content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"File read error: {e}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file.")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail=f"File '{original_filename}' is empty (0 bytes).")

    # Save to disk
    try:
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file on server.")

    # 1. Extract text
    try:
        blocks = load_document(saved_path, original_filename)
    except Exception as e:
        # Cleanup file if loading failed
        if saved_path.exists():
            saved_path.unlink()
        logger.error(f"Extraction error for '{original_filename}': {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract text from document: {str(e)}",
        )

    if not blocks:
        if saved_path.exists():
            saved_path.unlink()
        raise HTTPException(
            status_code=400,
            detail=f"No readable content could be extracted from '{original_filename}'.",
        )

    # Calculate page count if applicable
    max_page = 0
    pages_list = []
    for b in blocks:
        p = b.get("page")
        if p:
            max_page = max(max_page, p)
            pages_list.append({
                "page": p,
                "text": b.get("text", "")[:400] + ("..." if len(b.get("text", "")) > 400 else "")
            })

    total_pages = max_page if max_page > 0 else None

    # 2. Chunking
    chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))

    try:
        chunks = create_chunks_for_document(
            document_id=document_id,
            filename=original_filename,
            blocks=blocks,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    except Exception as e:
        logger.error(f"Chunking error: {e}")
        raise HTTPException(status_code=500, detail=f"Text chunking failed: {str(e)}")

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document text could not be divided into valid chunks.",
        )

    # 3. Generate embeddings
    try:
        chunk_texts = [c["text"] for c in chunks]
        embeddings = embed_batch(chunk_texts)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}",
        )

    # 4. Store in Vector Store
    try:
        add_chunks_to_vector_store(chunks, embeddings)
    except Exception as e:
        logger.error(f"Vector store error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to index embeddings in vector database: {str(e)}",
        )

    # 5. Save document metadata
    file_type_label = ext.replace(".", "").upper()
    doc_info = {
        "id": document_id,
        "filename": original_filename,
        "file_type": file_type_label,
        "file_size": format_file_size(len(content)),
        "file_size_bytes": len(content),
        "pages": total_pages,
        "chunks_count": len(chunks),
        "status": "Ready",
        "upload_time": datetime.now().isoformat(),
        "preview_pages": pages_list[:10],
        "full_preview_snippet": blocks[0]["text"][:600] if blocks else "",
        "file_path": str(saved_path),
    }

    add_document(doc_info)

    logger.info(
        f"Document '{original_filename}' ingested successfully. {len(chunks)} chunks stored."
    )

    return JSONResponse(
        status_code=200,
        content={
            "document_id": document_id,
            "filename": original_filename,
            "file_type": file_type_label,
            "pages": total_pages,
            "chunks_count": len(chunks),
            "status": "Ready",
            "message": f"Successfully extracted and indexed {len(chunks)} chunks.",
        },
    )


@router.get("/documents")
def get_documents_list():
    """Returns list of all ingested documents."""
    return list_documents()


@router.get("/documents/{document_id}")
def get_document_details(document_id: str):
    """Returns details and preview for a specific document."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.get("/documents/{document_id}/chunks")
def get_document_chunks(document_id: str):
    """Returns all stored chunks for a document from vector store."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = get_document_chunks_from_vector_store(document_id)
    return {
        "document_id": document_id,
        "filename": doc.get("filename", ""),
        "total_chunks": len(chunks),
        "chunks": chunks,
    }


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    """Deletes a document from disk, vector store, and registry."""
    doc = remove_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Delete chunks from vector store
    delete_document_from_vector_store(document_id)

    # Delete physical file
    file_path = doc.get("file_path")
    if file_path:
        try:
            p = Path(file_path)
            if p.exists():
                p.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file {file_path}: {e}")

    return {
        "status": "success",
        "message": f"Document '{doc.get('filename')}' and its vector embeddings deleted.",
    }


@router.post("/documents/{document_id}/clear")
def clear_document_chunks(document_id: str):
    """Clears indexed chunks for a document."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    deleted = delete_document_from_vector_store(document_id)
    doc["chunks_count"] = 0
    doc["status"] = "Cleared"
    add_document(doc)

    return {
        "status": "success",
        "message": f"Cleared {deleted} chunks for '{doc.get('filename')}'.",
    }
