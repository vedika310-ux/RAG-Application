"""Local JSON-based document metadata registry for persistence across restarts."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR / "data"
REGISTRY_FILE = DATA_DIR / "documents_registry.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    """Loads document registry from disk."""
    if not REGISTRY_FILE.exists():
        initial_data = {"documents": {}, "questions_count": 0}
        _save_registry(initial_data)
        return initial_data

    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading document registry: {e}")
        return {"documents": {}, "questions_count": 0}


def _save_registry(data: Dict[str, Any]) -> None:
    """Saves document registry to disk."""
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving document registry: {e}")


def list_documents() -> List[Dict[str, Any]]:
    """Returns all registered documents."""
    reg = _load_registry()
    docs = list(reg.get("documents", {}).values())
    # Sort by upload time descending
    docs.sort(key=lambda d: d.get("upload_time", ""), reverse=True)
    return docs


def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves document metadata by id."""
    reg = _load_registry()
    return reg.get("documents", {}).get(document_id)


def add_document(doc_data: Dict[str, Any]) -> None:
    """Registers or updates a document."""
    reg = _load_registry()
    doc_id = doc_data["id"]
    reg.setdefault("documents", {})[doc_id] = doc_data
    _save_registry(reg)


def remove_document(document_id: str) -> Optional[Dict[str, Any]]:
    """Removes a document from registry."""
    reg = _load_registry()
    if document_id in reg.get("documents", {}):
        doc = reg["documents"].pop(document_id)
        _save_registry(reg)
        return doc
    return None


def increment_question_count() -> int:
    """Increments the total questions asked counter."""
    reg = _load_registry()
    current = reg.get("questions_count", 0) + 1
    reg["questions_count"] = current
    _save_registry(reg)
    return current


def get_total_questions_count() -> int:
    """Returns total questions asked."""
    reg = _load_registry()
    return reg.get("questions_count", 0)
