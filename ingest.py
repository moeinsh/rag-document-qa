#!/usr/bin/env python3
"""CLI entry point: build the document index from data/*.pdf.

Usage:
    python ingest.py
"""
from app.pipeline import ingest

if __name__ == "__main__":
    stats = ingest()
    print(
        f"Indexed {stats['documents']} documents, {stats['pages']} pages, "
        f"{stats['chunks']} chunks -> {stats['index_dir']}"
    )
