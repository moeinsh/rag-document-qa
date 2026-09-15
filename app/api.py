"""FastAPI service for the DocuChat RAG app.

Endpoints:
    POST /ingest  — (re)build the index from data/*.pdf
    POST /ask      — ask a question against the indexed documents
    GET  /documents — list indexed documents
    GET  /         — the single-page chat UI
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.embeddings import Embedder
from app.pipeline import ingest as run_ingest
from app.qa import OpenAICompatibleLLM, answer_question
from app.store import DocStore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="DocuChat — chat with your PDFs", version="1.0.0")

_store: DocStore | None = None
_embedder: Embedder | None = None
_llm: OpenAICompatibleLLM | None = None


def get_store() -> DocStore:
    global _store
    if _store is None:
        try:
            _store = DocStore.load(settings.index_dir)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=503,
                detail="No index built yet. POST /ingest first.",
            ) from exc
    return _store


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder(settings.embedding_model)
    return _embedder


def get_llm() -> OpenAICompatibleLLM | None:
    global _llm
    if settings.llm_backend == "openai" and settings.openai_api_key:
        if _llm is None:
            _llm = OpenAICompatibleLLM(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                base_url=settings.openai_base_url,
            )
        return _llm
    return None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(default=settings.top_k, ge=1, le=10)


@app.get("/")
def ui_root():
    return FileResponse(os.path.join(BASE_DIR, "ui", "index.html"))


@app.post("/ingest")
def ingest_endpoint():
    global _store
    stats = run_ingest()
    _store = None  # force reload of the fresh index
    return {"status": "ok", **stats}


@app.get("/documents")
def documents():
    return {"documents": get_store().documents()}


@app.post("/ask")
def ask(req: AskRequest):
    store = get_store()
    embedder = get_embedder()
    qvec = embedder.encode_one(req.question)
    ranked = store.search(qvec, top_k=req.top_k)
    result = answer_question(
        req.question,
        ranked,
        llm_backend=settings.llm_backend,
        llm=get_llm(),
    )
    return {"question": req.question, **result}
