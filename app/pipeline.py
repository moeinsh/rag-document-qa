"""Ingestion pipeline: PDF -> pages -> chunks -> embeddings -> index on disk."""
from __future__ import annotations

import glob
import os

from app.chunking import chunk_text
from app.config import settings
from app.embeddings import Embedder
from app.store import DocStore


def read_pdf_pages(path: str) -> list[str]:
    """Extract plain text per page from a PDF."""
    from pypdf import PdfReader

    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return pages


def ingest(
    docs_dir: str | None = None,
    index_dir: str | None = None,
    embedder: Embedder | None = None,
) -> dict:
    docs_dir = docs_dir or settings.docs_dir
    index_dir = index_dir or settings.index_dir
    embedder = embedder or Embedder(settings.embedding_model)

    pdf_paths = sorted(glob.glob(os.path.join(docs_dir, "*.pdf")))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDFs found in {docs_dir}")

    store = DocStore()
    total_pages = 0
    for pdf_path in pdf_paths:
        doc_id = os.path.splitext(os.path.basename(pdf_path))[0]
        title = doc_id.replace("_", " ").title()
        pages = read_pdf_pages(pdf_path)
        total_pages += len(pages)

        chunks: list[dict] = []
        for page_no, page_text in enumerate(pages, start=1):
            chunks.extend(
                chunk_text(
                    page_text,
                    doc_id=doc_id,
                    title=title,
                    page=page_no,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )
            )
        if chunks:
            embeddings = embedder.encode([c["text"] for c in chunks])
            store.add(chunks, embeddings)

    store.save(index_dir)
    return {
        "documents": len(pdf_paths),
        "pages": total_pages,
        "chunks": len(store.chunks),
        "index_dir": index_dir,
    }


if __name__ == "__main__":
    stats = ingest()
    print(f"Indexed {stats['documents']} documents, {stats['pages']} pages, "
          f"{stats['chunks']} chunks -> {stats['index_dir']}")
