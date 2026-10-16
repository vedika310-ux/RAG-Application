"""Embedding service using Sentence Transformers."""
import os
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

_model_instance = None
_current_model_name = None


def get_embedding_model(model_name: str = DEFAULT_MODEL_NAME):
    """
    Singleton loader for SentenceTransformer model.
    """
    global _model_instance, _current_model_name
    if _model_instance is not None and _current_model_name == model_name:
        return _model_instance

    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading SentenceTransformer embedding model: {model_name}")
        # Try local cache first for fast offline startup
        try:
            _model_instance = SentenceTransformer(model_name, local_files_only=True)
        except Exception:
            _model_instance = SentenceTransformer(model_name)
        _current_model_name = model_name
        logger.info(f"Embedding model '{model_name}' successfully loaded.")
        return _model_instance
    except Exception as e:
        logger.error(f"Failed to load SentenceTransformer model '{model_name}': {str(e)}")
        raise RuntimeError(
            f"Failed to initialize embedding model '{model_name}'. Error: {str(e)}"
        )


def embed_text(text: str, model_name: str = DEFAULT_MODEL_NAME) -> List[float]:
    """
    Generates a normalized embedding vector for a single string.
    """
    model = get_embedding_model(model_name)
    vector = model.encode(text, normalize_embeddings=True)
    if isinstance(vector, np.ndarray):
        return vector.tolist()
    return list(vector)


def embed_batch(texts: List[str], model_name: str = DEFAULT_MODEL_NAME) -> List[List[float]]:
    """
    Generates normalized embedding vectors for a batch of strings.
    """
    if not texts:
        return []
    model = get_embedding_model(model_name)
    vectors = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    if isinstance(vectors, np.ndarray):
        return vectors.tolist()
    return [v.tolist() if isinstance(v, np.ndarray) else list(v) for v in vectors]
