"""Central configuration for the DocuChat RAG app."""
from __future__ import annotations

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    # --- Embeddings ---
    embedding_model: str = os.environ.get("DOCCHAT_EMBED_MODEL", "all-MiniLM-L6-v2")

    # --- Chunking ---
    chunk_size: int = int(os.environ.get("DOCCHAT_CHUNK_SIZE", "450"))      # words
    chunk_overlap: int = int(os.environ.get("DOCCHAT_CHUNK_OVERLAP", "90"))  # words

    # --- Retrieval ---
    top_k: int = int(os.environ.get("DOCCHAT_TOP_K", "4"))

    # --- Paths ---
    docs_dir: str = os.environ.get("DOCCHAT_DOCS_DIR", os.path.join(BASE_DIR, "data"))
    index_dir: str = os.environ.get("DOCCHAT_INDEX_DIR", os.path.join(BASE_DIR, "index"))

    # --- Answering ---
    # "extractive" (default, no API key needed) or "openai" (generative, needs key)
    llm_backend: str = os.environ.get("DOCCHAT_LLM", "extractive")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_model: str = os.environ.get("DOCCHAT_MODEL", "gpt-4o-mini")
    openai_base_url: str = os.environ.get(
        "DOCCHAT_BASE_URL", "https://api.openai.com/v1"
    )  # any OpenAI-compatible endpoint works


settings = Settings()
