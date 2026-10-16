"""PDF Loader using pypdf."""
import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if not text:
        return ""
    # Replace non-breaking spaces and irregular whitespace
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple consecutive newlines to maximum 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple inline spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def load_pdf(file_path: Path, filename: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF file.
    """
    try:
        reader = PdfReader(str(file_path))
    except Exception as e:
        raise ValueError(f"Failed to read PDF file '{filename}': {str(e)}")

    total_pages = len(reader.pages)
    if total_pages == 0:
        raise ValueError(f"PDF file '{filename}' has 0 pages.")

    blocks: List[Dict[str, Any]] = []

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        try:
            raw_text = page.extract_text() or ""
        except Exception:
            raw_text = ""

        cleaned = clean_text(raw_text)
        if cleaned:
            blocks.append({
                "text": cleaned,
                "page": page_num,
                "section": f"Page {page_num}",
                "metadata": {
                    "page": page_num,
                    "total_pages": total_pages,
                }
            })

    if not blocks:
        raise ValueError(
            f"No extractable text found in '{filename}'. It may be a scanned image-only PDF."
        )

    return blocks
