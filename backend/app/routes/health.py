"""Health check and system metrics route."""
from fastapi import APIRouter
from ..services.document_store import list_documents, get_total_questions_count
from ..vector_store import get_total_chunks_count
from ..embeddings import DEFAULT_MODEL_NAME

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """
    Returns system health status and statistics for the dashboard cards.
    """
    docs = list_documents()
    chunks_count = get_total_chunks_count()
    questions_count = get_total_questions_count()

    return {
        "status": "healthy",
        "documents_count": len(docs),
        "chunks_count": chunks_count,
        "questions_count": questions_count,
        "embedding_model": DEFAULT_MODEL_NAME,
        "vector_store": "ChromaDB (Persistent)",
    }
