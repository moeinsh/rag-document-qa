# DocuChat — Chat with Your PDFs (RAG Q&A App)

A retrieval-augmented Q&A app: drop in PDFs, ask questions in plain English,
get answers **with source citations** (document + page number). Runs fully
locally — no API key needed.

## Architecture

```
                        ┌─────────────────────────┐
  data/*.pdf ──ingest──▶│  pypdf → page text       │
                        │  chunk (450w, 90w overlap)│
                        │  sentence-transformers    │──▶ index/ (chunks.json + embeddings.npz)
                        │  (all-MiniLM-L6-v2)       │
                        └─────────────┬───────────┘
                                      │
  ┌─────────┐   POST /ask   ┌─────────▼───────────┐
  │ ui/     │ ────────────▶│  FastAPI              │
  │ index   │◀──────────── │  embed query → cosine │
  │ .html   │   answer +   │  top-k retrieval →    │
  └─────────┘   citations  │  extractive answer    │
                           │  (or pluggable LLM)   │
                           └───────────────────────┘
```

## How it works

1. **Ingest** (`python ingest.py`): each PDF's pages are extracted with
   pypdf, split into overlapping word chunks (450 words, 90 overlap), and
   embedded locally with `sentence-transformers` (all-MiniLM-L6-v2).
   Chunk text + normalized vectors are saved to `index/`.
2. **Retrieve** (`POST /ask`): the question is embedded with the same model
   and compared against every chunk by cosine similarity (exact NumPy
   dot-product — fast and dependency-light at this scale; a FAISS index
   could be dropped in later without changing the API).
3. **Answer**: the default **extractive** mode quotes the top retrieved
   chunks verbatim, each with a numbered citation `[1]`, `[2]` … pointing
   at document title and page. Every claim is traceable to a source.

## Run it

```bash
pip install -r requirements.txt

# 1. create the sample PDFs (fictional docs for the demo)
python make_sample_pdfs.py

# 2. run the end-to-end demo (ingest + 3 questions, no API key needed)
python demo.py        # transcript saved to demo_output.txt

# 3. start the API + chat UI
uvicorn app.api:app --reload
# open http://127.0.0.1:8000  → ask questions in the chat UI
# POST /ingest  → rebuild the index after adding your own PDFs to data/
```

## Plugging in an LLM (optional)

Extractive mode is the default and needs nothing. For fluent generative
answers grounded on the same retrieved chunks:

```bash
export DOCCHAT_LLM=openai
export OPENAI_API_KEY=sk-...
# optional:
export DOCCHAT_MODEL=gpt-4o-mini
export DOCCHAT_BASE_URL=https://api.openai.com/v1   # any OpenAI-compatible endpoint
uvicorn app.api:app --reload
```

The generative path uses a strict grounding system prompt ("answer using
ONLY the excerpts; cite every claim like [1]") and reuses the identical
retrieval + citation pipeline — only the final wording step changes.

## Project layout

```
app/
  config.py      all knobs (chunk size, model, top_k, LLM backend) via env vars
  chunking.py    overlapping word chunker with provenance metadata
  embeddings.py  sentence-transformers wrapper (L2-normalized vectors)
  store.py       chunk store + cosine retrieval + npz/json persistence
  pipeline.py    PDF → pages → chunks → embeddings → index
  qa.py          extractive answerer + pluggable OpenAI-compatible LLM
  api.py         FastAPI: /ingest, /ask, /documents, / (chat UI)
ui/index.html    single-page chat UI (vanilla JS, no build step)
make_sample_pdfs.py  generates the 3 fictional demo PDFs
ingest.py        CLI: build the index
demo.py          CLI: end-to-end demo → demo_output.txt
```

## Scope & limitations (honest)

- The bundled demo answers **extractively** — it quotes your documents
  rather than writing new prose. That's deliberate: citations stay exact.
- Retrieval quality depends on the embedding model; `all-MiniLM-L6-v2` is
  a good general-purpose default, not magic. Very long or scanned/image
  PDFs need OCR (not included) before ingestion.
- The sample PDFs (`data/`) are **fictional documents generated for this
  demo** — a fake product manual, a fake employee handbook, a fake support
  FAQ. No real companies, no real data.
- This is a demonstration sample showing a RAG workflow end to end —
  chunking, local embeddings, retrieval, cited answers, and a clean API —
  not a production deployment (no auth, no rate limiting, single process).

## Demo transcript

See [`demo_output.txt`](demo_output.txt) — a real run: 3 PDFs ingested
(3 documents, 3 pages, 3 chunks), 3 questions answered, every answer
citing document title, page, and relevance score. All three questions
retrieved the correct source document as the top hit.
