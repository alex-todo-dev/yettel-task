from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from app.rag_engine import load_chunks, build_embeddings, build_index, MODEL_NAME, retrieve
from pydantic import BaseModel                                                                                                                                                                                   
from openai import OpenAI     
from dotenv import load_dotenv                                                                                                                                                                                   

load_dotenv()                                                                                                                                                                                                                                                                                                                                                                    
                                       
state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    chunks = load_chunks()
    model = SentenceTransformer(MODEL_NAME)
    embeddings = build_embeddings(chunks)
    index = build_index(embeddings)
    state["chunks"] = chunks
    state["model"] = model
    state["index"] = index
    yield
    state.clear()

app = FastAPI(lifespan=lifespan)

client = OpenAI()
                                                                                                                                                                                                                   
class AskRequest(BaseModel):
    query: str                                                                                                                                                                                                   
                  
class AskResponse(BaseModel):               
    answer: str                         

@app.post("/ask", response_model=AskResponse)                                                                                                                                                                    
async def ask(request: AskRequest):
    chunks = retrieve(request.query, state["chunks"], state["index"], state["model"])                                                                                                                            
    context = "\n\n".join(c["text"] for c in chunks)
                                              
    response = client.chat.completions.create(
        model="gpt-4o-mini",                                                                                                                                                                                     
        messages=[                                                                                                                                                                                               
              {"role": "system", "content": "You are a Yettel customer support assistant. Answer based only on the provided context."},                                                                            
              {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.query}"}                                                                                                                     
          ]                               
      )                                                                                                                                                                                                            
                                                                                                                                                                                                               
    return AskResponse(answer=response.choices[0].message.content)  