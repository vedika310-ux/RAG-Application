"""CSV Loader using pandas."""
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd


def load_csv(file_path: Path, filename: str) -> List[Dict[str, Any]]:
    """
    Reads tabular CSV data and creates structured text blocks preserving column names.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    df = None

    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except Exception:
            continue

    if df is None or df.empty:
        raise ValueError(f"CSV file '{filename}' is empty or could not be parsed.")

    # Fill NaN values with empty string or 'N/A'
    df = df.fillna("N/A")

    columns = [str(c) for c in df.columns]
    total_rows = len(df)
    batch_size = 15  # Group rows into manageable chunks

    blocks: List[Dict[str, Any]] = []

    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch_df = df.iloc[start_idx:end_idx]

        lines = [f"Columns: {', '.join(columns)}"]
        for row_i, row in batch_df.iterrows():
            row_items = [f"{col}: {row[col]}" for col in df.columns]
            lines.append(f"Row {row_i + 1}: " + " | ".join(row_items))

        chunk_text = "\n".join(lines)
        row_range_str = f"Rows {start_idx + 1}-{end_idx}"

        blocks.append({
            "text": chunk_text,
            "page": None,
            "section": row_range_str,
            "metadata": {
                "section": row_range_str,
                "row_range": f"{start_idx + 1}-{end_idx}",
                "total_rows": total_rows,
                "columns": columns
            }
        })

    return blocks
