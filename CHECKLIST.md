# Yettel AI Assistant — Project Checklist

## Setup
- [x] Create project structure and folders
- [x] Create `requirements.txt`
- [x] Create `.env.example`

## Implementation
- [x] `app/data_loader.py` — load PDFs, extract text, split into chunks
- [x] `app/rag_engine.py` — embeddings (sentence-transformers), FAISS vector store, retrieve()
- [x] `app/api.py` — FastAPI, POST /ask endpoint
- [x] Choose and integrate LLM

## Documentation
- [x] `README.md` — setup instructions, curl example, Solution Design section
- [x] Solution Design: Approach & Choices
- [x] Solution Design: Challenges & Limitations
- [x] Solution Design: Potential Improvements

## Bonus
- [x] `Dockerfile`

## Testing
- [x] Run API locally
- [x] Test queries against Yettel PDFs
- [x] Verify answers are relevant
