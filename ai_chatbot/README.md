# 🤖 AI Chatbot (Live!)

**Live Demo**: [https://ai-projects-challenge-aichatbotyq46ledde6l.streamlit.app/](https://ai-projects-challenge-aichatbotyq46ledde6l.streamlit.app/)

## Features
- Powered by **Groq + Llama 3.1** (instant responses)
- Built with **LangChain + Streamlit**
- Local Ollama support (optional)
- Clean, modular code

## Tech Stack
- `langchain-groq`, `streamlit`, `python-dotenv`
- Deployed on **Streamlit Community Cloud** (free)

## Local Run
```bash
pip install -r requirements.txt

cd backend
uvicorn main:app --reload

cd /ui
streamlit run app.py

# (Optional) Install Ollama for local LLM
# https://ollama.ai/download
ollama pull


