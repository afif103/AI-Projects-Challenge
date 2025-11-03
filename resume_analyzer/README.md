# AI Resume Analyzer


## What it does
Upload PDF resume → Ask questions like:
> "What are my Python skills?"
> "List my certifications"

## How it works
1. **PDF Parsing** → Extract text with PyPDF2
2. **Chunking** → Split into 500-token pieces
3. **Embeddings** → HuggingFace (all-MiniLM-L6-v2)
4. **Vector Store** → FAISS (local) or Pinecone
5. **RAG** → Retrieve + Generate with LangChain RetrievalQA
6. **LLM** → Ollama (llama3.2:3b) — 100% private

## Features
- **Input Safety** — Blocks jailbreaks, long prompts
- **Fallbacks** — FAISS if Pinecone fails
- **Cost Tracking** — $0.000012/query (OpenAI mode)
- **Local Mode** — No API keys, no data sent
- 
## Live Demo
[Try it now!](https://ai-projects-challenge-8rhfvfmompdb5urbnpysyn.streamlit.app/) 
> Upload your resume → Ask: *"What are my Python skills?"*

## Setup
```bash


# Create .env
cp .env.example .env
# Add your keys:
# USE_OPENAI=true
# OPENAI_API_KEY=sk-...
# USE_PINECONE=true
# PINECONE_API_KEY=pcsk_...

pip install -r requirements.txt
streamlit run app.py
