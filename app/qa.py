"""Answering layer.

Two modes, same interface:

1. ``extractive`` (default) — no API key needed. Returns the top retrieved
   chunks verbatim, each with a numbered citation ([1], [2], ...) pointing
   at document title + page. Honest by construction: every claim is
   traceable to a source chunk.

2. ``openai`` — generative answers from any OpenAI-compatible chat
   endpoint, grounded on the retrieved chunks. Requires OPENAI_API_KEY
   (and optionally DOCCHAT_MODEL / DOCCHAT_BASE_URL).
"""
from __future__ import annotations

import json
import urllib.request


# ---------------------------------------------------------------- extractive
def extractive_answer(question: str, ranked: list[tuple[dict, float]]) -> dict:
    """Build an answer out of the retrieved chunks, with citations."""
    sources = []
    parts = [
        f'Question: "{question}"',
        "",
        "Answer (extractive — quoted from your documents):",
        "",
    ]
    for i, (chunk, score) in enumerate(ranked, start=1):
        sources.append(
            {
                "n": i,
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "page": chunk["page"],
                "score": round(score, 3),
            }
        )
        parts.append(f"[{i}] {chunk['title']} — page {chunk['page']} (relevance {score:.2f})")
        parts.append(chunk["text"])
        parts.append("")
    parts.append(
        "Note: this is the built-in extractive mode (no LLM). "
        "Set DOCCHAT_LLM=openai with an API key for generative answers."
    )
    return {"mode": "extractive", "answer": "\n".join(parts).strip(), "sources": sources}


# ---------------------------------------------------------------- generative
class OpenAICompatibleLLM:
    """Minimal client for any OpenAI-compatible /v1/chat/completions endpoint.

    Uses only the stdlib (urllib) so plugging in an LLM adds no dependency.
    """

    SYSTEM_PROMPT = (
        "You answer questions using ONLY the document excerpts provided below. "
        "Every factual claim in your answer must end with a citation like [1], [2] "
        "referring to the numbered excerpts. If the excerpts do not contain the "
        "answer, say so explicitly instead of guessing."
    )

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, question: str, ranked: list[tuple[dict, float]]) -> str:
        context = "\n\n".join(
            f"[{i}] ({chunk['title']}, page {chunk['page']})\n{chunk['text']}"
            for i, (chunk, _) in enumerate(ranked, start=1)
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Document excerpts:\n{context}\n\nQuestion: {question}",
                },
            ],
            "temperature": 0.2,
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
        return body["choices"][0]["message"]["content"].strip()


def generative_answer(
    question: str, ranked: list[tuple[dict, float]], llm: OpenAICompatibleLLM
) -> dict:
    answer = llm.generate(question, ranked)
    sources = [
        {
            "n": i,
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "page": chunk["page"],
            "score": round(score, 3),
        }
        for i, (chunk, score) in enumerate(ranked, start=1)
    ]
    return {"mode": "generative", "answer": answer, "sources": sources}


# ---------------------------------------------------------------- dispatcher
def answer_question(
    question: str,
    ranked: list[tuple[dict, float]],
    llm_backend: str = "extractive",
    llm: OpenAICompatibleLLM | None = None,
) -> dict:
    if not ranked:
        return {
            "mode": llm_backend,
            "answer": "I couldn't find anything relevant in the indexed documents.",
            "sources": [],
        }
    if llm_backend == "openai" and llm is not None:
        return generative_answer(question, ranked, llm)
    return extractive_answer(question, ranked)
