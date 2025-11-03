# ==============================================================
# AI RESUME ANALYZER — MODERN & SAFE VERSION (2025 READY)
# Includes: Pinecone (new SDK), FAISS fallback, safety filters,
# cost tracking, efficient RAG pipeline, local-friendly mode
# ==============================================================

import streamlit as st
import os
import re
from dotenv import load_dotenv

# LangChain & community imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI, Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Pinecone new SDK
from pinecone import Pinecone, ServerlessSpec

# Load environment
load_dotenv()

# Load from Streamlit Cloud secrets (if deployed)
if "PINECONE_API_KEY" in st.secrets:
    os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["PINECONE_INDEX"] = st.secrets.get("PINECONE_INDEX", "resume-index")

# ==============================================================
# CONFIGURATION
# ==============================================================

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

# Safety / validation rules
BLOCKED_WORDS = ["hack", "jailbreak", "ignore", "system", "bypass", "prompt"]
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

# ==============================================================
# STREAMLIT UI
# ==============================================================

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("📄 AI Resume Analyzer")
st.write("**Upload your resume (PDF)** → Ask professional questions about it!")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# ==============================================================
# PDF Processing
# ==============================================================

if uploaded_file:
    try:
        import tempfile

        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        # Now load with PyPDFLoader
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        # Embeddings (OpenAI or HuggingFace)
        @st.cache_resource
        def get_embeddings():
            try:
                if USE_OPENAI:
                    st.info("Using OpenAI Embeddings (text-embedding-3-small)")
                    return OpenAIEmbeddings(model="text-embedding-3-small")
                else:
                    st.info("Using HuggingFace Local Embeddings (free)")
                    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            except Exception as e:
                st.warning(f"Embedding load failed: {e}")
                return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        embeddings = get_embeddings()

        # ==============================================================
        # VECTOR STORE (PINECONE OR FAISS)
        # ==============================================================

        with st.spinner("Indexing your resume..."):
            try:
                if USE_PINECONE:
                    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                    index_name = os.getenv("PINECONE_INDEX", "resume-index")

                    # Check if index exists
                    if index_name not in pc.list_indexes().names():
                        st.info("Creating Pinecone index (may take a few seconds)...")
                        pc.create_index(
                            name=index_name,
                            dimension=1536,
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                        )

                    from langchain_community.vectorstores import Pinecone as PineconeStore
                    vectorstore = PineconeStore.from_documents(chunks, embeddings, index_name=index_name)
                    st.success("✅ Pinecone vector store ready!")
                else:
                    vectorstore = FAISS.from_documents(chunks, embeddings)
                    st.success("✅ FAISS vector store ready! (Local mode)")

            except Exception as e:
                st.warning(f"Pinecone failed: {e}. Falling back to FAISS.")
                vectorstore = FAISS.from_documents(chunks, embeddings)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # ==============================================================
        # LLM SETUP
        # ==============================================================

        @st.cache_resource
        def get_llm():
            try:
                if USE_OPENAI:
                    return OpenAI(model="gpt-4o-mini", temperature=0.2)
                else:
                    return Ollama(model="llama3.2:3b", temperature=0.2)
            except Exception as e:
                st.error(f"LLM init failed: {e}")
                return Ollama(model="llama3.2:3b", temperature=0.2)

        llm = get_llm()

        # ==============================================================
        # PROMPT TEMPLATE
        # ==============================================================

        prompt_template = """You are a professional HR analyst.
Answer ONLY based on the provided resume content.
If something is missing, reply: "Not mentioned in resume."
Be concise, factual, and professional.

Context:
{context}

Question:
{question}

Answer:"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # ==============================================================
        # RETRIEVAL CHAIN
        # ==============================================================

        def answer_question(question):
            docs = retriever.invoke(question)
            context = "\n\n".join([d.page_content for d in docs])
            chain = PROMPT | llm
            return chain.invoke({"context": context, "question": question})

        st.success("✅ Resume ready for Q&A!")

        # ==============================================================
        # Q&A SECTION
        # ==============================================================

        question = st.text_input(
            "Ask a question about your resume:",
            placeholder="Example: What programming languages do I know?",
            max_chars=MAX_QUESTION_LEN
        )

        if question:
            if not is_safe_input(question):
                st.error("⚠️ Invalid or unsafe input. Keep it short and professional.")
                st.stop()

            with st.spinner("Analyzing your resume..."):
                try:
                    answer = answer_question(question)
                except Exception as e:
                    st.error(f"AI failed to respond: {e}")
                    st.stop()

            st.markdown("### 💬 Answer:")
            st.write(answer)

            # Optional: cost tracking (for OpenAI)
            if USE_OPENAI:
                input_tokens = len(question.split()) * 1.3
                output_tokens = len(str(answer).split()) * 1.3
                cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
                st.caption(f"💰 **Estimated cost:** ${cost:.6f} (gpt-4o-mini)")

        # ==============================================================
        # MODE DISPLAY
        # ==============================================================

        mode = (
            "OpenAI + Pinecone"
            if USE_OPENAI and USE_PINECONE
            else "OpenAI + FAISS"
            if USE_OPENAI
            else "Local (Ollama + FAISS)"
        )
        st.caption(f"**Mode:** {mode} | **Security:** Active | **Optimized for low cost**")

    except Exception as e:
        st.error(f"❌ Failed to process PDF: {e}. Try a text-based PDF (not scanned).")

