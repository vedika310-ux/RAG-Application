"""API routes package."""
from .health import router as health_router
from .documents import router as documents_router
from .rag import router as rag_router

__all__ = ["health_router", "documents_router", "rag_router"]
