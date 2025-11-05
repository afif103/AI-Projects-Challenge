import streamlit as st
import os

# Streamlit Secrets (MUST HAVE GROQ_API_KEY)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("🚨 Missing GROQ_API_KEY in Secrets! Add it in Manage app > Settings > Secrets.")
    st.stop()

# Imports (AFTER checking key)
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    print("✅ All imports successful!")
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Prompt
prompt_template = PromptTemplate.from_template(
    """You are a helpful, concise AI assistant.

Context: {context}

User: {user_input}

Assistant: """
)

# Chain
@st.cache_resource
def create_chain():
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.7
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain

# UI
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 AI Chatbot")
st.caption("Powered by Groq + LangChain")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chain = create_chain()
            response = chain.invoke({
                "user_input": prompt,
                "context": ""
            })
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

st.sidebar.markdown("---")
st.sidebar.markdown("**Status:** ✅ Live with Groq!")