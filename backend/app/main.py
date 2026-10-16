"""FastAPI application entrypoint for RAG Document Intelligence."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag_windows")

from .routes.health import router as health_router
from .routes.documents import router as documents_router
from .routes.rag import router as rag_router
from .vector_store import get_collection

app = FastAPI(
    title="RAG Document Intelligence",
    description="High-performance Document Question-Answering RAG API for Windows 11",
    version="1.0.0",
)

# CORS Configuration for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(rag_router)


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing RAG Document Intelligence System...")
    # Initialize / verify Chroma collection
    try:
        col = get_collection()
        logger.info(f"ChromaDB ready. Total chunks indexed: {col.count()}")
    except Exception as e:
        logger.error(f"Vector store startup notice: {e}")

    logger.info("RAG Backend is running and ready for queries.")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
