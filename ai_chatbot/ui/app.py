# ui/app.py - FULL APP (Backend + UI for Streamlit Cloud)
"""
AI Chatbot - Deployed to Streamlit Cloud
Uses Groq (fast, free) - Local Ollama for dev
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq  # ← For cloud
from langchain_community.llms import Ollama  # ← For local
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env (if exists)
load_dotenv()

# Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USE_LOCAL = not GROQ_API_KEY  # Auto-detect: local if no key

# Prompt
prompt_template = PromptTemplate.from_template(
    """You are a helpful, concise AI assistant.

Context: {context}

User: {user_input}

Assistant: """
)

# Chain Factory
@st.cache_resource
def create_chain():
    if USE_LOCAL:
        # Local Ollama
        llm = Ollama(
            model="llama3.2:3b",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        st.info("🖥️ Using Local Ollama")
    else:
        # Cloud Groq
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",  # Fast & smart
            temperature=0.7
        )
        st.info("☁️ Using Groq Cloud (Fast & Free)")
    
    chain = prompt_template | llm | StrOutputParser()
    return chain

# Streamlit UI
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 AI Chatbot")
st.caption(f"Powered by {'Ollama (Local)' if USE_LOCAL else 'Groq + LangChain'}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chain = create_chain()
            try:
                response = chain.invoke({
                    "user_input": prompt,
                    "context": ""
                })
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Sidebar: Instructions
with st.sidebar:
    st.header("🚀 Deployed!")
    if USE_LOCAL:
        st.warning("💡 Add GROQ_API_KEY to .env for cloud deploy")
    st.markdown("---")
    st.markdown("[GitHub Repo](https://github.com/yourname/ai-chatbot)")