
import re
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from config.settings import MAX_INPUT_CHARS, BANNED_WORDS
import tempfile
import os

def clean_text(text: str) -> str:
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    for word in BANNED_WORDS:
        text = re.sub(rf'\b{word}\b', '[REDACTED]', text, flags=re.IGNORECASE)
    return text

def load_from_text(text: str) -> str:
    text = clean_text(text)
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS] + "\n\n[Content truncated]"
    return text

def load_from_url(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=' ')
        return load_from_text(text)
    except Exception as e:
        raise ValueError(f"Failed to scrape URL: {str(e)}")

def load_from_pdf_file(uploaded_file) -> str:
    """Use PyPDFLoader to extract text from uploaded PDF"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Use LangChain PyPDFLoader
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        text = "\n".join([page.page_content for page in pages])

        # Clean up
        os.unlink(tmp_path)

        return load_from_text(text)
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")
