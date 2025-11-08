# ui/app.py
import streamlit as st
from backend.agents.recommender import get_recommendations

st.set_page_config(page_title="AI Recommender", layout="wide")
st.title("AI Movie Recommender")
st.caption("Llama 3.2 + RAG — 100% Local")

with st.sidebar:
    profile = st.text_area("Profile:", "I love sci-fi and AI", height=100)
    st.caption("Ollama must be running: `ollama run llama3.2:3b`")

col1, col2 = st.columns([3,1])
with col1:
    query = st.text_input("Query:", "Recommend a movie")
with col2:
    st.write(""); st.write("")
    btn = st.button("Get Recs", type="primary")

if btn:
    with st.spinner("Thinking..."):
        result = get_recommendations(profile, query)
    
    if result.get("recommendations"):
        st.success("Recommendations:")
        for r in result["recommendations"]:
            with st.expander(f"**{r.get('title')}** — {r.get('score', 0):.2f}"):
                st.write(r.get("reason"))
    else:
        st.error(f"Error: {result.get('reason')}")
        st.info("Run: `python -m backend.db.ingest` and `ollama run llama3.2:3b`")