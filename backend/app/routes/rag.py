"""RAG query and settings routes."""
import os
import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from ..retrieval import retrieve_relevant_chunks, build_context_from_sources
from ..llm import generate_answer
from ..services.document_store import increment_question_count
from ..embeddings import DEFAULT_MODEL_NAME

logger = logging.getLogger(__name__)
router = APIRouter(tags=["RAG"])


class AskRequest(BaseModel):
    question: str = Field(..., description="The user's query")
    document_id: Optional[str] = Field(
        None, description="Specific document ID to query, or 'all' / null for entire knowledge base"
    )
    top_k: Optional[int] = Field(None, description="Number of chunks to retrieve (default: TOP_K from env)")


class SourceItem(BaseModel):
    document: str
    document_id: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    row_range: Optional[str] = None
    chunk_id: str
    score: float
    text: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    retrieval_count: int
    queried_document_id: Optional[str] = None


class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    top_k: Optional[int] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    """
    RAG Question-Answering Pipeline:
    1. Validates user question
    2. Embeds question using SentenceTransformers
    3. Retrieves top-K semantically relevant chunks from ChromaDB
    4. Computes similarity scores
    5. Formulates structured context
    6. Calls Gemini LLM with strict context-only constraints
    7. Returns answer and source citations
    """
    cleaned_q = request.question.strip()
    if not cleaned_q:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Determine Top-K
    effective_top_k = request.top_k or int(os.getenv("TOP_K", "5"))
    effective_doc_id = request.document_id if request.document_id and request.document_id != "all" else None

    # Step 1 & 2 & 3: Retrieve relevant chunks
    try:
        sources = retrieve_relevant_chunks(
            question=cleaned_q,
            top_k=effective_top_k,
            document_id=effective_doc_id,
        )
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Vector search failed: {str(e)}",
        )

    # Step 4: If no sources retrieved at all
    if not sources:
        return AskResponse(
            answer="I could not find enough information in the uploaded documents to answer this question.",
            sources=[],
            retrieval_count=0,
            queried_document_id=request.document_id,
        )

    # Step 5: Build context
    context = build_context_from_sources(sources)

    # Step 6: Generate answer from LLM
    try:
        answer = generate_answer(question=cleaned_q, context=context)
    except Exception as e:
        logger.error(f"LLM error: {e}")
        answer = f"Failed to generate answer from LLM: {str(e)}"

    # Increment question metric counter
    increment_question_count()

    formatted_sources = [
        SourceItem(
            document=s.get("document", "Unknown"),
            document_id=s.get("document_id"),
            page=s.get("page"),
            section=s.get("section"),
            row_range=s.get("row_range"),
            chunk_id=s.get("chunk_id", ""),
            score=s.get("score", 0.0),
            text=s.get("text", ""),
        )
        for s in sources
    ]

    return AskResponse(
        answer=answer,
        sources=formatted_sources,
        retrieval_count=len(sources),
        queried_document_id=request.document_id,
    )


@router.get("/settings")
def get_settings():
    """Returns current server configuration."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    key_configured = bool(api_key and api_key != "your_api_key_here" and api_key != "your_gemini_api_key_here")

    # Masked key preview
    masked_key = ""
    if key_configured and len(api_key) > 8:
        masked_key = api_key[:4] + "..." + api_key[-4:]
    elif key_configured:
        masked_key = "********"

    return {
        "gemini_api_key_configured": key_configured,
        "gemini_api_key_preview": masked_key,
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "top_k": int(os.getenv("TOP_K", "5")),
        "chunk_size": int(os.getenv("CHUNK_SIZE", "800")),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "100")),
        "embedding_model": DEFAULT_MODEL_NAME,
    }


@router.post("/settings")
def update_settings(update: SettingsUpdate):
    """Updates runtime configuration settings."""
    if update.gemini_api_key is not None:
        key = update.gemini_api_key.strip()
        os.environ["GEMINI_API_KEY"] = key
    if update.gemini_model:
        os.environ["GEMINI_MODEL"] = update.gemini_model.strip()
    if update.top_k is not None and update.top_k > 0:
        os.environ["TOP_K"] = str(update.top_k)
    if update.chunk_size is not None and update.chunk_size > 50:
        os.environ["CHUNK_SIZE"] = str(update.chunk_size)
    if update.chunk_overlap is not None and update.chunk_overlap >= 0:
        os.environ["CHUNK_OVERLAP"] = str(update.chunk_overlap)

    return {"status": "success", "message": "Settings updated successfully."}
