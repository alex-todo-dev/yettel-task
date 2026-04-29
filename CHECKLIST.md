# Yettel AI Assistant — Project Checklist

## Setup
- [ ] Create project structure and folders
- [ ] Create `requirements.txt`
- [ ] Create `.env.example`

## Implementation
- [ ] `app/data_loader.py` — load PDFs, extract text, split into chunks
- [ ] `app/rag_engine.py` — embeddings (sentence-transformers), FAISS vector store, retrieve()
- [ ] `app/api.py` — FastAPI, POST /ask endpoint
- [ ] Choose and integrate LLM

## Documentation
- [ ] `README.md` — setup instructions, curl example, Solution Design section
- [ ] Solution Design: Approach & Choices
- [ ] Solution Design: Challenges & Limitations
- [ ] Solution Design: Potential Improvements

## Bonus
- [ ] `Dockerfile`

## Testing
- [ ] Run API locally
- [ ] Test queries against Yettel PDFs
- [ ] Verify answers are relevant
