"""Document loaders package for RAG application."""
from pathlib import Path
from typing import List, Dict, Any

from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .text_loader import load_text
from .csv_loader import load_csv
from .markdown_loader import load_markdown

LOADER_MAPPING = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_text,
    ".csv": load_csv,
    ".md": load_markdown,
    ".markdown": load_markdown,
}


def load_document(file_path: str | Path, filename: str) -> List[Dict[str, Any]]:
    """
    Extracts text sections and pages from a file.
    Returns a list of structured blocks:
    [
        {
            "text": "...",
            "page": 1,          # Optional: 1-indexed page number
            "section": "...",   # Optional: section heading or row info
            "metadata": {...}
        }
    ]
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in LOADER_MAPPING:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported formats: {', '.join(LOADER_MAPPING.keys())}"
        )

    loader = LOADER_MAPPING[ext]
    return loader(path, filename)
