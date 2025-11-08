# app.py
import streamlit as st, os, json
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough

# === UI ===
st.set_page_config(page_title="AI Recommender", layout="wide")
st.title("AI Movie Recommender")
st.caption("Llama 3.2 + RAG — LangChain 1.x + ChatPromptTemplate")

profile = st.sidebar.text_area("Your taste:", "I love sci-fi, AI, and mind-bending plots", height=100)
query = st.text_input("Ask:", "Recommend a movie")
if st.button("Get Recommendations", type="primary"):
    with st.spinner("Thinking..."):
        # === EMBEDDINGS & DB ===
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # === LLM (Groq) ===
        llm = ChatGroq(model="llama-3.2-3b-preview", groq_api_key=os.getenv("GROQ_API_KEY"), temperature=0.3)

        # === CHAT PROMPT TEMPLATE (MODERN 1.X STYLE) ===
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a movie recommendation expert. Return ONLY valid JSON."),
            ("human", "Profile: {profile}\nQuery: {input}\n\nRelevant items:\n{context}\n\n"
                      "Return: {{\"recommendations\": [{{title, score, reason}}, ...]}}")
        ])

        # === CHAIN ===
        chain = (
            {"context": retriever | (lambda docs: "\n".join([f"{d.metadata.get('title','?')}: {d.page_content}" for d in docs])),
             "profile": RunnablePassthrough(), "input": RunnablePassthrough()}
            | prompt
            | llm
            | JsonOutputParser()
        )

        # === INVOKE ===
        result = chain.invoke({"input": query, "profile": profile})

        # === DISPLAY ===
        if recs := result.get("recommendations", [])[:3]:
            st.success(f"Top {len(recs)} picks:")
            for r in recs:
                with st.expander(f"**{r.get('title','?')}** — {r.get('score',0):.2f}"):
                    st.write(r.get("reason", "No reason"))
        else:
            st.error("No matches found.")