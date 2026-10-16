"""Plain text loader with resilient Windows encoding support."""
import re
from pathlib import Path
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Normalize linebreaks and excessive whitespace."""
    if not text:
        return ""
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def load_text(file_path: Path, filename: str) -> List[Dict[str, Any]]:
    """
    Reads plain text files using multiple encoding fallbacks.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "iso-8859-1", "utf-16"]
    content = None

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"Could not decode text file '{filename}' with supported encodings.")

    cleaned = clean_text(content)
    if not cleaned:
        raise ValueError(f"Text file '{filename}' is empty.")

    # Split into logical sections/paragraphs if very long
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]

    blocks: List[Dict[str, Any]] = []
    # If small or moderately sized, keep as coherent chunks
    current_chunk = []
    current_len = 0

    for i, p in enumerate(paragraphs):
        current_chunk.append(p)
        current_len += len(p)
        if current_len >= 1200 or i == len(paragraphs) - 1:
            blocks.append({
                "text": "\n\n".join(current_chunk),
                "page": None,
                "section": f"Section {len(blocks) + 1}",
                "metadata": {
                    "section": f"Section {len(blocks) + 1}"
                }
            })
            current_chunk = []
            current_len = 0

    return blocks
