# backend/src/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env from project root


class Settings:
    MODEL_NAME = "ollama/llama3.2:3b"  # ← YOUR MODEL
    OLLAMA_BASE_URL = "http://localhost:11434"

settings = Settings()

