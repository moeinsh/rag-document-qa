#!/usr/bin/env python3
"""End-to-end demo: ingest the sample PDFs, ask 3 questions, print answers.

Saves the full transcript to demo_output.txt. Runs with NO API key —
the built-in extractive mode answers from retrieved chunks with citations.
"""
import io
import os

from app.config import settings
from app.embeddings import Embedder
from app.pipeline import ingest
from app.qa import answer_question
from app.store import DocStore

BASE = os.path.dirname(os.path.abspath(__file__))

QUESTIONS = [
    "What is the warranty period for the Nimbus Home Hub?",
    "How many paid vacation days do Northwind employees get per year?",
    "How do I factory reset the Nimbus Home Hub?",
]


def run_demo() -> str:
    buf = io.StringIO()
    out = lambda *a: (print(*a), print(*a, file=buf))  # noqa: E731

    out("=" * 70)
    out("DocuChat demo — retrieval-augmented Q&A over sample PDFs")
    out("=" * 70)

    # 1. ingest
    stats = ingest()
    out(f"\n[ingest] {stats['documents']} documents, {stats['pages']} pages, "
        f"{stats['chunks']} chunks indexed.\n")

    # 2. load + embedder
    store = DocStore.load(settings.index_dir)
    embedder = Embedder(settings.embedding_model)

    # 3. ask
    for n, question in enumerate(QUESTIONS, 1):
        out("-" * 70)
        out(f"Q{n}: {question}")
        out("-" * 70)
        ranked = store.search(embedder.encode_one(question), top_k=settings.top_k)
        result = answer_question(question, ranked, llm_backend="extractive")
        out(result["answer"])
        out("")

    transcript = buf.getvalue()
    out_path = os.path.join(BASE, "demo_output.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"\n[demo] transcript saved to {out_path}")
    return transcript


if __name__ == "__main__":
    run_demo()
