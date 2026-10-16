"""Markdown Loader preserving heading hierarchy."""
import re
from pathlib import Path
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Normalize line endings and whitespace."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_markdown(file_path: Path, filename: str) -> List[Dict[str, Any]]:
    """
    Parses markdown files into sections based on headings (#, ##, ###).
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    content = None

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if content is None:
        raise ValueError(f"Could not read markdown file '{filename}'.")

    content = clean_text(content)
    if not content:
        raise ValueError(f"Markdown file '{filename}' is empty.")

    lines = content.split("\n")
    blocks: List[Dict[str, Any]] = []

    current_section = "Overview"
    current_lines: List[str] = []

    def flush_section():
        nonlocal current_lines
        if current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                blocks.append({
                    "text": text,
                    "page": None,
                    "section": current_section,
                    "metadata": {
                        "section": current_section
                    }
                })
            current_lines = []

    heading_regex = re.compile(r"^(#{1,6})\s+(.+)$")

    for line in lines:
        match = heading_regex.match(line)
        if match:
            flush_section()
            current_section = match.group(2).strip()
            current_lines.append(line)
        else:
            current_lines.append(line)

    flush_section()

    if not blocks:
        blocks.append({
            "text": content,
            "page": None,
            "section": "Overview",
            "metadata": {"section": "Overview"}
        })

    return blocks
