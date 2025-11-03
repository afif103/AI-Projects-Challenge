# AI Resume Analyzer  
**Ask your resume anything — powered by RAG, OpenAI, Pinecone, and Ollama**  
[Live Demo](https://ai-projects-challenge-8rhfvfmompdb5urbnpysyn.streamlit.app/) 

---

## Features
- **PDF Resume Upload** → Extract text with `PyPDFLoader`
- **RAG Pipeline** → Retrieve relevant chunks using **FAISS** or **Pinecone**
- **Dual LLM Support**:
  - **OpenAI (gpt-4o-mini)** → Fast, accurate, cost-tracked
  - **Ollama (llama3.2:3b)** → Free, local, private
- **Smart Fallbacks**:
  - OpenAI quota exceeded → Auto-switch to local mode
  - Pinecone fails → FAISS fallback
- **Security**:
  - Input sanitization
  - No personal data leakage
  - `.env` + Streamlit secrets
- **Cost Tracking** → Real-time OpenAI usage ($0.000012/query)

---

## Tech Stack
| Component        | Tool |
|------------------|------|
| Frontend         | Streamlit |
| LLM              | OpenAI, Ollama |
| Embeddings       | OpenAI, HuggingFace |
| Vector DB        | Pinecone, FAISS |
| PDF Processing   | PyPDFLoader |
| Orchestration    | LangChain |
| Deployment       | Streamlit Cloud |

---

## Live Demo
[Try it now!](https://ai-projects-challenge-8rhfvfmompdb5urbnpysyn.streamlit.app/)  
> Upload your resume → Ask: *"What are my Python skills?"*

---

## Setup (Local)

```bash
git clone https://github.com/afif103/6-AI-Projects-Challenge.git
cd 6-AI-Projects-Challenge/resume_analyzer

# Create .env
cp .env.example .env
# Add your keys:
# USE_OPENAI=true
# OPENAI_API_KEY=sk-...
# USE_PINECONE=true
# PINECONE_API_KEY=pcsk_...

pip install -r requirements.txt
streamlit run app.py
