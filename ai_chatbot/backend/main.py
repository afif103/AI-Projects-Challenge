# backend/main.py
"""
AI Chatbot Backend - Local LLM (Ollama)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.chains import create_chat_chain
import os

# Disable LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "false"

app = FastAPI(title="AI Chatbot (Local)", version="1.0")

class ChatRequest(BaseModel):
    user_input: str
    context: str = ""

class ChatResponse(BaseModel):
    response: str

chain = create_chat_chain()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty")
    
    try:
        result = await chain.ainvoke({
            "user_input": request.user_input,
            "context": request.context
        })
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}