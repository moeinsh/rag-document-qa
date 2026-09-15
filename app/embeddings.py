"""Local embeddings via sentence-transformers (no API key required)."""
from __future__ import annotations

import numpy as np


class Embedder:
    """Thin wrapper around a SentenceTransformer model.

    Vectors are L2-normalized on the way out, so cosine similarity
    reduces to a dot product at retrieval time.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(
            texts, show_progress_bar=False, normalize_embeddings=True
        )
        return np.asarray(vecs, dtype=np.float32)

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]
