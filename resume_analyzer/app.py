# ==============================================================
# AI RESUME ANALYZER — MODERN & SAFE VERSION (2025 READY)
# Includes:
#  - Pinecone (v4 SDK) + FAISS fallback
#  - OpenAI quota and key handling
#  - Safety filters & validation
#  - Cost tracking for OpenAI usage
#  - Fully local fallback (HuggingFace + Ollama)
# ==============================================================

import streamlit as st
import os
import re
import tempfile
from dotenv import load_dotenv

# LangChain community imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI, Ollama
from langchain_core.prompts import PromptTemplate

# Pinecone (new SDK)
from pinecone import Pinecone, ServerlessSpec

# ==============================================================
# ENVIRONMENT CONFIGURATION
# ==============================================================

load_dotenv()

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

# Safety / validation rules
BLOCKED_WORDS = ["hack", "jailbreak", "ignore", "system", "bypass", "prompt"]
MAX_QUESTION_LEN = 200
MIN_QUESTION_LEN = 3


def is_safe_input(text: str) -> bool:
    """Rejects unsafe or malformed inputs."""
    text = text.strip().lower()
    if len(text) < MIN_QUESTION_LEN or len(text) > MAX_QUESTION_LEN:
        return False
    if any(word in text for word in BLOCKED_WORDS):
        return False
    if re.search(r"[<>(){}\[\]]{3,}", text):
        return False
    return True


# ==============================================================
# STREAMLIT PAGE CONFIG
# ==============================================================

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("📄 AI Resume Analyzer")
st.write("**Upload your resume (PDF)** → Ask professional questions about it!")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# ==============================================================
# MAIN APP LOGIC
# ==============================================================

if uploaded_file:
    try:
        # -------------------------
        # 1️⃣  PDF Extraction
        # -------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)

        # -------------------------
        # 2️⃣  Embeddings
        # -------------------------
        @st.cache_resource
        def get_embeddings():
            try:
                if USE_OPENAI:
                    st.info("🔗 Using OpenAI embeddings (text-embedding-3-small)...")
                    return OpenAIEmbeddings(model="text-embedding-3-small")
                else:
                    st.info("🧠 Using local HuggingFace embeddings (free)...")
                    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            except Exception as e:
                err = str(e).lower()
                if "insufficient_quota" in err or "429" in err:
                    st.error("🚫 OpenAI API quota exceeded. Switching to local mode.")
                elif "api key" in err or "unauthorized" in err:
                    st.error("🔑 Invalid OpenAI API key. Using local fallback.")
                else:
                    st.warning(f"⚠️ Embedding error: {e}")
                return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        embeddings = get_embeddings()

        # -------------------------
        # 3️⃣  Vector Store (Pinecone or FAISS)
        # -------------------------
        with st.spinner("🔍 Indexing your resume..."):
            try:
                if USE_PINECONE:
                    st.info("Connecting to Pinecone...")
                    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                    index_name = os.getenv("PINECONE_INDEX", "resume-index")

                    # Create index if missing
                    existing = [i["name"] for i in pc.list_indexes()]
                    if index_name not in existing:
                        st.info("Creating new Pinecone index (this may take a few seconds)...")
                        pc.create_index(
                            name=index_name,
                            dimension=1536,
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                        )

                    # Get index handle
                    index = pc.Index(index_name)

                    from langchain_community.vectorstores import Pinecone as PineconeStore
                    vectorstore = PineconeStore.from_documents(chunks, embeddings, index_name=index_name)
                    st.success("✅ Pinecone vector store ready!")

                else:
                    vectorstore = FAISS.from_documents(chunks, embeddings)
                    st.success("✅ FAISS vector store ready! (Local mode)")

            except Exception as e:
                err = str(e)
                if "quota" in err or "api key" in err:
                    st.warning("⚠️ Pinecone API issue or quota exceeded. Switching to FAISS.")
                else:
                    st.warning(f"Pinecone failed: {e}. Falling back to FAISS.")
                vectorstore = FAISS.from_documents(chunks, embeddings)

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # -------------------------
        # 4️⃣  LLM SETUP
        # -------------------------
        @st.cache_resource
        def get_llm():
            try:
                if USE_OPENAI and os.getenv("OPENAI_API_KEY"):
                    return OpenAI(model="gpt-4o-mini", temperature=0.2)
                else:
                    raise ValueError("OpenAI key missing or quota exceeded")
            except Exception as e:
                st.warning(f"OpenAI failed ({e}), switching to Ollama (local).")
                return Ollama(model="llama3.2:3b", temperature=0.2)

        llm = get_llm()

        # -------------------------
        # 5️⃣  Prompt Template
        # -------------------------
        prompt_template = """You are a professional HR analyst.
Answer ONLY using the resume text provided.
If information is missing, respond with: "Not mentioned in resume."
Keep answers concise, factual, and professional.

Context:
{context}

Question:
{question}

Answer:"""

        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

        # -------------------------
        # 6️⃣  Retrieval Chain
        # -------------------------
        def answer_question(question):
            try:
                docs = retriever.invoke(question)
                context = "\n\n".join([d.page_content for d in docs])
                chain = PROMPT | llm
                return chain.invoke({"context": context, "question": question})
            except Exception as e:
                err = str(e).lower()
                if "insufficient_quota" in err or "429" in err:
                    st.error("🚫 Your OpenAI API quota has been exceeded. Please check billing or switch to local mode.")
                elif "api key" in err:
                    st.error("🔑 Invalid OpenAI API key. Update your .env file.")
                else:
                    st.error(f"❌ AI failed: {e}")
                return "Error: Unable to generate response."

        st.success("✅ Resume processed successfully! Ready for Q&A.")

        # -------------------------
        # 7️⃣  Q&A Section
        # -------------------------
        question = st.text_input(
            "Ask something about your resume:",
            placeholder="Example: What programming languages do I know?",
            max_chars=MAX_QUESTION_LEN,
        )

        if question:
            if not is_safe_input(question):
                st.error("⚠️ Invalid or unsafe input. Keep it short and professional.")
                st.stop()

            with st.spinner("Analyzing your resume..."):
                answer = answer_question(question)

            st.markdown("### 💬 Answer:")
            st.write(answer)

            # Cost tracking for OpenAI mode
            if USE_OPENAI:
                input_tokens = len(question.split()) * 1.3
                output_tokens = len(str(answer).split()) * 1.3
                cost = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
                st.caption(f"💰 **Estimated cost:** ${cost:.6f} (gpt-4o-mini)")

        # -------------------------
        # 8️⃣  Mode Display
        # -------------------------
        mode = (
            "OpenAI + Pinecone"
            if USE_OPENAI and USE_PINECONE
            else "OpenAI + FAISS"
            if USE_OPENAI
            else "Local (Ollama + FAISS)"
        )
        st.caption(f"**Mode:** {mode} | **Security:** Active | **Optimized for low cost**")

  
    except Exception as e:
        error_text = str(e)

        # Detect OpenAI quota or rate-limit errors
        if "insufficient_quota" in error_text or "You exceeded your current quota" in error_text:
            st.error(
            "🚫 **OpenAI quota exceeded** — you've used up your API credit or free tier limit.\n\n"
            "Please check your [OpenAI Billing Dashboard](https://platform.openai.com/account/billing) "
            "and either add payment or switch to local mode (Ollama)."
            )

        # Detect Pinecone quota or auth errors
        elif "Pinecone" in error_text and "API key" in error_text:
            st.error(
            "🔑 **Pinecone API key missing or invalid** — double-check your `.env` file or Streamlit secrets."
            )

        # Detect scanned/non-text PDFs
        elif "file" in error_text.lower() and "pdf" in error_text.lower():
            st.error("📄 The uploaded file seems to be a scanned (image-based) PDF. Please upload a text-based resume instead.")

        # General fallback
        else:
            st.error(f"❌ Failed to process PDF: {e}")
