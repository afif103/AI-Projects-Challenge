# 🤖 AI Chatbot (LangChain + LangSmith + Streamlit)

**Local, Private, Observable AI Chatbot**  
Built with **separation of concerns**: Backend (FastAPI + LangChain) ↔ Frontend (Streamlit)

---

## 🚀 Live Demo (Local)

```bash
http://localhost:8501


🛡️ Privacy & Safety

100% Local Processing Option: Use LOCAL_LLM=true + Ollama/LM Studio
No User Data Stored
LangSmith Tracing (Optional, Opt-Out via .env)
Input Sanitized & Rate-Limited


▶️ Run Locally
1. Clone & Setup

git clone https://github.com/yourname/ai-chatbot.git
cd ai-chatbot
cp .env.example .env


2. Get API Keys

OpenAI API Key
LangSmith API Key

Paste into .env
3. Run with Docker (Recommended)

docker-compose up --build

UI: http://localhost:8501
API: http://localhost:8000

4. Or Run Separately

# Terminal 1 - Backend
cd backend && uvicorn main:app --reload

# Terminal 2 - UI
cd ui && streamlit run app.py

🔍 LangSmith Tracing
All chains are traced:


https://smith.langchain.com/projects/p/ai-chatbot-local

Evaluate prompts, latency, and correctness.

🧪 Test Chain

cd backend && pytest tests/
