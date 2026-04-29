from app.data_loader import load_pdf_files, chunk_pages, DATA_DIR
import re
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def load_chunks() -> list[dict]:
    documents = load_pdf_files(DATA_DIR)
    chunks = chunk_pages(documents)
    return chunks


def _clean_filename(name: str) -> str:
    name = name.replace(".pdf", "")
    name = re.sub(r"[_\d\.\-]+$", "", name)
    return name.strip()


def build_embeddings(chunks: list[dict]) -> np.ndarray:
    model = SentenceTransformer(MODEL_NAME)
    texts = [
        f"{_clean_filename(c['file_name'])} | {c['sub_title'] or ''}\n{c['text']}"
        for c in chunks
    ]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings


                                                                                                                                                                                                                   
def build_index(embeddings: np.ndarray) -> faiss.Index:                                                                                                                                                          
    dim = embeddings.shape[1]                                                                                                                                                                                    
    index = faiss.IndexFlatL2(dim)                                                                                                                                                                               
    index.add(embeddings)                                                                                                                                                                                        
    return index

def retrieve(query: str, chunks: list[dict], index: faiss.Index, model: SentenceTransformer, top_k: int = 3, max_distance: float = 16.5) -> list[dict]:
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for d, i in zip(distances[0], indices[0]) if d < max_distance]                                                                                                                                                                       
                                             