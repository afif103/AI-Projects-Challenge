# backend/loader.py
# Handles secure PDF loading using LangChain's PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from config.settings import MAX_RESUME_PAGES, MIN_TEXT_LENGTH, MAX_TEXT_LENGTH
import tempfile
import os

def load_resume_pdf(pdf_file) -> str:
    """
    Securely loads PDF from uploaded file, extracts text, and applies limits.
    Uses temporary file to avoid memory issues.
    """
    try:
        # Step 1: Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.getvalue())   # Write bytes from Streamlit upload
            tmp_path = tmp.name              # Get path for loader

        # Step 2: Use LangChain PyPDFLoader (robust, handles encrypted PDFs)
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()[:MAX_RESUME_PAGES]  # Limit pages

        # Step 3: Clean up temp file immediately
        os.unlink(tmp_path)

        # Step 4: Combine text from all pages
        text = "\n".join([p.page_content for p in pages]).strip()

        # Step 5: Input validation
        if len(text) < MIN_TEXT_LENGTH:
            raise ValueError("Resume too short. Please upload a detailed resume.")
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH] + "\n... [truncated]"  # Prevent overflow

        return text

    except Exception as e:
        # Step 6: Wrap any error in user-friendly message
        raise ValueError(f"Failed to read PDF: {str(e)}")
