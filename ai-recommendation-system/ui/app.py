# ui/app.py
import sys
import os
# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from backend.agents.recommender import get_recommendations

st.set_page_config(page_title="AI Movie Recommender", layout="wide")

st.title("🤖 AI Movie Recommender")
st.caption("Powered by Llama 3.2 + RAG (100% Local)")

with st.sidebar:
    st.header("User Profile")
    profile = st.text_area("Tell me about your taste:", "I love sci-fi, AI, and mind-bending plots.", height=100)

    st.divider()
    st.caption("Local Mode: Ollama + Chroma")

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("Ask for a recommendation:", "Recommend a movie")

with col2:
    st.write("")
    st.write("")
    recommend_btn = st.button("Get Recommendations", type="primary", use_container_width=True)

if recommend_btn:
    with st.spinner("Thinking..."):
        result = get_recommendations(profile=profile, query=query)
    
    if "recommendations" in result and result["recommendations"]:
        st.success(f"Here are your top {len(result['recommendations'])} recommendations:")
        for rec in result["recommendations"]:
            with st.expander(f"**{rec.get('title', 'Unknown')}** — Score: {rec.get('score', 0):.2f}"):
                st.write(rec.get("reason", "No reason provided"))
    else:
        st.error(f"No recommendations: {result.get('reason', 'Unknown error')}")
        st.info("Troubleshoot: Run `python -m backend.db.ingest` to load data. Ensure Ollama is running with `ollama run llama3.2:3b`.")
