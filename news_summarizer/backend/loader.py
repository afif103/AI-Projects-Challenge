# backend/loader.py
import re
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from config.settings import MAX_INPUT_CHARS, BANNED_WORDS

def clean_text(text: str) -> str:
    """Sanitize input: remove URLs, emails, banned words"""
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove emails
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Redact banned words
    for word in BANNED_WORDS:
        text = re.sub(rf'\b{word}\b', '[REDACTED]', text, flags=re.IGNORECASE)
    return text

def load_from_text(text: str) -> str:
    text = clean_text(text)
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS] + "\n\n[Content truncated due to length]"
    return text

def load_from_url(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts/styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ')
        return load_from_text(text)
    except Exception as e:
        raise ValueError(f"Failed to scrape URL: {str(e)}")