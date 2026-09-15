"""Document store: chunk metadata + embedding matrix + cosine retrieval.

FAISS is intentionally *not* required — for a portfolio-scale corpus
(hundreds of chunks) a normalized dot-product over a NumPy matrix is
fast, dependency-light, and exact. The interface is small enough that a
FAISS index could be dropped in later without touching the API.
"""
from __future__ import annotations

import json
import os

import numpy as np


class DocStore:
    def __init__(self) -> None:
        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None  # shape (n_chunks, dim), L2-normalized

    # -- mutation ------------------------------------------------------
    def add(self, chunks: list[dict], embeddings: np.ndarray) -> None:
        if self.embeddings is None:
            self.chunks = list(chunks)
            self.embeddings = np.asarray(embeddings, dtype=np.float32)
        else:
            self.chunks.extend(chunks)
            self.embeddings = np.vstack([self.embeddings, embeddings]).astype(np.float32)

    # -- retrieval -----------------------------------------------------
    def search(self, query_vec: np.ndarray, top_k: int = 4) -> list[tuple[dict, float]]:
        """Return the top_k (chunk, cosine_score) pairs, best first."""
        if self.embeddings is None or not self.chunks:
            return []
        scores = self.embeddings @ np.asarray(query_vec, dtype=np.float32)
        k = min(top_k, len(self.chunks))
        idx = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in idx]

    # -- persistence ---------------------------------------------------
    def save(self, index_dir: str) -> None:
        os.makedirs(index_dir, exist_ok=True)
        np.savez_compressed(
            os.path.join(index_dir, "embeddings.npz"),
            embeddings=self.embeddings if self.embeddings is not None else np.zeros((0, 0)),
        )
        with open(os.path.join(index_dir, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=1)

    @classmethod
    def load(cls, index_dir: str) -> "DocStore":
        store = cls()
        emb_path = os.path.join(index_dir, "embeddings.npz")
        chunks_path = os.path.join(index_dir, "chunks.json")
        if not (os.path.exists(emb_path) and os.path.exists(chunks_path)):
            raise FileNotFoundError(f"No index found in {index_dir} — run ingest.py first.")
        store.embeddings = np.load(emb_path)["embeddings"].astype(np.float32)
        with open(chunks_path, encoding="utf-8") as f:
            store.chunks = json.load(f)
        return store

    # -- introspection -------------------------------------------------
    def documents(self) -> list[dict]:
        seen: dict[str, dict] = {}
        for ch in self.chunks:
            d = seen.setdefault(
                ch["doc_id"], {"doc_id": ch["doc_id"], "title": ch["title"], "chunks": 0}
            )
            d["chunks"] += 1
        return sorted(seen.values(), key=lambda d: d["doc_id"])
