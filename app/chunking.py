"""Word-based chunking with overlap for RAG ingestion."""
from __future__ import annotations


def chunk_text(
    text: str,
    doc_id: str,
    title: str,
    page: int = 1,
    chunk_size: int = 450,
    chunk_overlap: int = 90,
) -> list[dict]:
    """Split *text* into overlapping word chunks.

    Each chunk carries its provenance (document id, title, page) so answers
    can cite exactly where they came from.
    """
    words = text.split()
    if not words:
        return []

    chunks: list[dict] = []
    step = max(chunk_size - chunk_overlap, 1)
    start = 0
    idx = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(
            {
                "id": f"{doc_id}#p{page}c{idx}",
                "doc_id": doc_id,
                "title": title,
                "page": page,
                "text": " ".join(words[start:end]),
            }
        )
        idx += 1
        if end == len(words):
            break
        start += step
    return chunks
