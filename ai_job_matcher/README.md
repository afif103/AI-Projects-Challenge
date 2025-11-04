# AI Job Matcher

**Match your resume to any job in seconds — 100% private, free, and GPU-accelerated.**

Upload your resume → Paste job description → Get:
- Match Score (0–100%)
- Missing Skills
- 3 AI-Powered Resume Edits
- Downloadable PDF Report

---

## LIVE DEMO  
[https://ai-projects-challenge-aijobmatcher000ermp3tfcrbcrbih.streamlit.app/](https://ai-projects-challenge-aijobmatcher000ermp3tfcrbcrbih.streamlit.app/)

---

## Features

| Feature | Status |
|-------|--------|
| GPU-Accelerated Embeddings | `CUDA` |
| Online-First (Best Accuracy) | `all-mpnet-base-v2` |
| Local LLM Fallback | `Ollama (llama3.2)` |
| Vector DB | `FAISS` |
| PDF Report | `Helvetica` |
| 100% Private | No API keys, no data sent |

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: LangChain, HuggingFace, Ollama
- **Embeddings**: `all-mpnet-base-v2` (GPU)
- **Vector Store**: FAISS (local)
- **PDF**: `fpdf` (Helvetica, no font files)
- **LLM**: Local Ollama (private)
- **Deployment**: Streamlit Cloud

---

## How to Run Locally

```bash
# 1. Clone
git clone https://github.com/afif103/ai-job-matcher.git
cd ai-job-matcher

# 2. Install
pip intellectuelle install -r requirements.txt

# 3. Run
streamlit run app.py
