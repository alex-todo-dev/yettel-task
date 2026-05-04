# Yettel AI Assistant

A RAG-based AI assistant for Yettel customer support agents. Answers questions about plans and services from internal PDF documents.

## Setup

1. Clone the repository and navigate to the project folder.

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Export your OpenAI API key:
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

4. Start the API server:
```bash
uvicorn app.api:app --reload
```

5. Start the Gradio chat interface (in a separate terminal):
```bash
python gradio_app.py
```

Open `http://localhost:7860` in your browser to use the chat UI.

## Docker

Build and run both the API and the Gradio interface in a single container:

```bash
docker build -t yettel-rag .
docker run -p 8000:8000 -p 7860:7860 -e OPENAI_API_KEY=your_openai_api_key_here yettel-rag
```

| Service | URL |
|---|---|
| REST API | http://localhost:8000 |
| Gradio Chat UI | http://localhost:7860 |

## Example Query

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Как се активира услугата 100-те национални обекта?"}'
```

Response:
```json
{"answer": "Услугата се активира чрез банер в приложението или от менюто Услуги..."}
```

## Solution Design

### Approach & Choices

- **PDF parsing**: `pypdf` — lightweight, no external dependencies, sufficient for text-based PDFs.
- **Chunking strategy**: Question-to-question splitting. The documents are structured as Q&A pairs with section headers in all-caps. Each chunk contains one question and its answer, with the section subtitle stored as metadata. This preserves semantic coherence and improves retrieval precision.
- **Embedding model**: `paraphrase-multilingual-MiniLM-L12-v2` from sentence-transformers. Chosen for its multilingual support (documents are in Bulgarian), small size, and good semantic similarity quality.
- **Vector store**: FAISS `IndexFlatL2` — exact search, simple, no configuration needed. At 89 chunks, approximate search provides no benefit.
- **LLM**: OpenAI `gpt-4o-mini` — fast, cost-effective, and sufficient for answer synthesis from retrieved context.

### Challenges & Limitations

- **PDF text extraction**: `pypdf` wraps long lines across multiple lines, breaking question detection. Handled by detecting continuations via lowercase-start or short-length heuristics.
- **Language**: The documents are in Bulgarian. A multilingual embedding model is required — a monolingual English model would produce poor retrieval results.
- **No persistent index**: The FAISS index is rebuilt on every server startup. For 89 chunks this takes a few seconds, but would not scale to large document sets.

### Potential Improvements

**Data & Indexing**
- **Persistent index**: Save the FAISS index and embeddings to disk so startup is instant. Add a checksum or timestamp so the index auto-invalidates when source files change.
- **Decoupled reindex**: Split data loading from the app startup. A background job (cron or Celery) rebuilds the index and hot-swaps it in without downtime. The API keeps serving the old index until the new one is ready.
- **Upload endpoint**: Add a `POST /sources` endpoint to upload new PDF documents. It saves the file and triggers a reindex job, returning immediately without blocking the API.
- **Chunk overlap**: Some answers span section boundaries. 50–100 token overlap on the current 500-token chunks would reduce missed context.

**Retrieval Quality**
- **Reranking**: After FAISS retrieves the top-k candidates, run a cross-encoder (e.g. `cross-encoder/ms-marco-MiniLM`) to reorder results by relevance before sending to the LLM. Meaningfully improves answer quality with modest latency cost.
- **Hybrid retrieval**: Combine semantic search (FAISS) with keyword search (BM25) for better coverage of exact-match queries.

**API & Backend**
- **Streaming responses**: Use `stream=True` on the OpenAI call and Server-Sent Events on the FastAPI side. Gradio supports streaming natively — significant UX improvement for long answers.
- **"I don't know" fallback**: If no chunks pass the distance threshold, return a canned response instead of sending empty context to the LLM. Prevents hallucination on out-of-scope questions.
- **Conversation history**: The API currently has no memory between turns. Pass the conversation history in the request and include it in the OpenAI messages array for proper multi-turn support.
- **Health and metrics endpoints**: Expose `/health` and `/metrics` with index size, number of documents, and last reindex timestamp. Cheap to add and useful for monitoring.
