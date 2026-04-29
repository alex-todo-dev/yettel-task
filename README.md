# Yettel AI Assistant

A RAG-based AI assistant for Yettel customer support agents. Answers questions about plans and services from internal PDF documents.

## Setup

1. Clone the repository and navigate to the project folder.

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example and add your OpenAI API key:
```bash
cp .env.example .env
```

4. Start the API server:
```bash
uvicorn app.api:app --reload
```

## Docker (Optional)

Build and run with Docker:

```bash
docker build -t yettel-assistant .
docker run -p 8000:8000 --env-file .env yettel-assistant
```

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

- **Persistent index**: Save the FAISS index and embeddings to disk so startup is instant. Rebuild only when documents change.
- **Hybrid retrieval**: Combine semantic search (FAISS) with keyword search (BM25) for better coverage of exact-match queries.
- **Chunk overlap**: Some answers span section boundaries. Adding overlap between chunks would reduce missed context.
- **Streaming responses**: Stream the LLM response back to the client for faster perceived latency.
