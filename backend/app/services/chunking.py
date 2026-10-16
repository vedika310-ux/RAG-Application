"""Text chunking service with sentence-aware boundaries and rich metadata."""
import os
import re
from typing import List, Dict, Any


DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text into chunks of at most `chunk_size` characters,
    with `chunk_overlap` character overlap, attempting to preserve
    paragraph and sentence boundaries.
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    text_len = len(text)

    # Separators in preference order
    separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for natural breakpoint within the chunk window
        best_break = -1
        search_window = text[start:end]

        for sep in separators:
            last_pos = search_window.rfind(sep)
            # Require the breakpoint to be reasonably far into the chunk (at least 40% of chunk_size)
            if last_pos != -1 and last_pos >= int(chunk_size * 0.4):
                best_break = start + last_pos + len(sep)
                break

        if best_break == -1:
            # No natural separator found, slice at character boundary
            best_break = end

        chunk = text[start:best_break].strip()
        if chunk:
            chunks.append(chunk)

        # Advance start position taking overlap into account
        start = max(best_break - chunk_overlap, start + 1)

    return chunks


def create_chunks_for_document(
    document_id: str,
    filename: str,
    blocks: List[Dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Transforms extracted document blocks into granular, vector-ready chunks
    with full metadata.
    """
    all_chunks: List[Dict[str, Any]] = []
    chunk_counter = 0

    for block in blocks:
        block_text = block.get("text", "").strip()
        if not block_text:
            continue

        page = block.get("page")
        section = block.get("section")
        block_meta = block.get("metadata", {})

        # Sub-divide block text if it exceeds chunk_size
        text_slices = split_text_into_chunks(
            block_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        for slice_idx, slice_text in enumerate(text_slices):
            chunk_counter += 1
            chunk_id = f"chunk_{document_id[:8]}_{chunk_counter}"

            metadata = {
                "document_id": document_id,
                "filename": filename,
                "chunk_id": chunk_id,
                "chunk_index": chunk_counter,
                "page": page if page is not None else 0,  # 0 indicates non-paged
                "section": section or "",
                "row_range": block_meta.get("row_range", ""),
                "char_count": len(slice_text),
                "word_count": len(slice_text.split()),
            }

            all_chunks.append({
                "chunk_id": chunk_id,
                "text": slice_text,
                "metadata": metadata,
            })

    return all_chunks
