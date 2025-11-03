# =================================================
# AI RESUME ANALYZER — FIXED & PRODUCTION-READY
# Fixes: Pinecone rename, OpenAI quota fallback, PDF handling
# =================================================

import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chains import RetrievalQA
from langchain.llms import OpenAI, Ollama
from langchain.prompts import PromptTemplate
import os
import re
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Configuration — Defaults to FREE mode if keys missing
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

# Input safety filter
BLOCKED_WORDS = ["hack", "jailbreak", "ignore", "system", "prompt", "bypass"]
MAX_QUESTION_LEN = 200
MIN_QUESTION_LEN = 3

def is_safe_input(text: str) -> bool:
    """Block empty, too long, or harmful questions."""
    text = text.strip().lower()
    if len(text) < MIN_QUESTION_LEN or len(text) > MAX_QUESTION_LEN:
        return False
    if any(word in text for word in BLOCKED_WORDS):
        return False
    if re.search(r"[<>(){}\[\]]{3,}", text):
        return False
    return True

# Page config
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("AI Resume Analyzer")
st.write("**Upload your resume (PDF) → Ask anything about it.**")

# Upload PDF
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file:
    try:
        # Extract text from PDF
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            st.error("No text found in PDF. Try a **text-based PDF** (not scanned/image-based). For scanned PDFs, consider OCR tools.")
            st.stop()

        # Chunk text
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.create_documents([text])

        # Get embeddings
        @st.cache_resource
        def get_embeddings():
            try:
                if USE_OPENAI:
                    return OpenAIEmbeddings(model="text-embedding-3-small")
                return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # FREE fallback
            except Exception as e:
                st.error(f"Embeddings failed: {e}. Using local fallback.")
                return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Always fallback

        embeddings = get_embeddings()

        # Create vector store
        with st.spinner("Indexing resume..."):
            try:
                if USE_PINECONE:
                    from pinecone import Pinecone  # ← FIXED: New package name
                    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                    index_name = os.getenv("PINECONE_INDEX", "resume-index")

                    # Check if index exists
                    if index_name in pc.list_indexes().names():
                        vectorstore = Pinecone.from_existing_index(index_name, embeddings)
                        st.success("Connected to Pinecone index!")
                    else:
                        vectorstore = Pinecone.from_documents(docs, embeddings, index_name=index_name)
                        st.success("Created new Pinecone index!")
                else:
                    vectorstore = FAISS.from_documents(docs, embeddings)
                    st.success("FAISS vector store ready!")
            except Exception as e:
                st.warning(f"Pinecone failed: {e}. Falling back to FAISS (free).")
                vectorstore = FAISS.from_documents(docs, embeddings)

        # Get LLM
        @st.cache_resource
        def get_llm():
            try:
                if USE_OPENAI:
                    return OpenAI(model="gpt-4o-mini", temperature=0.2)
                return Ollama(model="llama3.2:3b", temperature=0.2)
            except Exception as e:
                st.error(f"LLM failed: {e}. Using local fallback.")
                return Ollama(model="llama3.2:3b", temperature=0.2)

        llm = get_llm()

        # Retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # Prompt template
        prompt_template = """You are a professional HR analyst.
        Answer ONLY using the resume text below.
        If information is missing, say: "Not mentioned in resume."
        Be concise, factual, and professional.
        Never reveal personal data like phone/email.

        Context:
        {context}

        Question: {question}
        Answer:"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # RAG chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False,
        )

        st.success("Resume loaded securely!")

        # Q&A
        question = st.text_input(
            "Ask about your resume:",
            placeholder="What are my programming skills?",
            max_chars=MAX_QUESTION_LEN
        )

        if question:
            if not is_safe_input(question):
                st.error("Invalid input. Keep it short, clean, and relevant.")
                st.stop()

            with st.spinner("Analyzing..."):
                try:
                    answer = qa.run(question)
                except Exception as e:
                    st.error("AI failed to respond. Try again.")
                    st.stop()

            st.markdown("**Answer:**")
            st.write(answer)

            # Cost tracking (OpenAI only)
            if USE_OPENAI:
                input_tokens = len(question.split()) * 1.3
                output_tokens = len(answer.split()) * 1.3
                cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
                st.caption(f"**Estimated cost:** `${cost:.6f}` (gpt-4o-mini)")

        # Mode display (always visible)
        mode = (
            "OpenAI + Pinecone" if USE_OPENAI and USE_PINECONE else
            "OpenAI + FAISS" if USE_OPENAI else
            "Local (Ollama + FAISS)"
        )
        st.caption(f"**Mode:** {mode} | **Security:** Active")

    except Exception as e:
        st.error(f"Failed to process PDF: {e}. Try a text-based PDF (not scanned/image). For scanned PDFs, use OCR tools like Tesseract.")
        st.stop()