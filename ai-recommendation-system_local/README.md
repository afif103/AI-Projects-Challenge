# AI Recommendation System

**Local-first, privacy-safe, LLM-powered** — built with **LangChain**, **Ollama/Groq**, **Chroma**, **Streamlit**.

---

## Features
- UI & Logic **fully separated**
- **Local LLM (Ollama)** or **Cloud (Groq)**
- **LangSmith tracing + evaluation**
- **Chroma (local)** / **Pinecone (cloud)**
- **Zero PII logging**

---

## Run in VS Code (Conda)

### 1. Create Environment
```bash
conda create -n recsys python=3.12 -y
conda activate recsys

python -m pip install --upgrade pip

pip install -r requirements.txt

pip uninstall pinecone-plugin-inference -y


$env:PYTHONPATH = (Get-Location).Path

python -m backend.db.ingest
streamlit run ui/app.py
