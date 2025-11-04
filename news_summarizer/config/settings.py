# config/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Models
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
LLM_MODEL = "llama3.2"
FAISS_INDEX_PATH = BASE_DIR / "faiss_index"

# Limits
MAX_INPUT_CHARS = 5000
MAX_OUTPUT_CHARS = 300
SUMMARY_SENTENCES = (3, 5)

# Safety
BANNED_WORDS = {
    "kill", "bomb", "terrorist", "hate", "nazi", "rape", "murder", "genocide",
    "fuck", "shit", "bitch", "asshole", "cunt", "faggot", "retard"
}

# UI
APP_TITLE = "News Summarizer – Daily AI News Digest"
APP_ICON = "📰"
BADGES = "🏆 GPU ACCELERATED • 🔒 Local • 💸 Free"