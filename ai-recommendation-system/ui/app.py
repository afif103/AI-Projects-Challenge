# ui/app.py
import sys
import os
# Add project root (ai-recommendation-system/) to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from backend.agents.recommender import get_recommendations

st.set_page_config(page_title="AI Recommender", layout="wide")
st.title("AI Movie Recommender")
st.caption("Llama 3.2 + RAG")

with st.sidebar:
    profile = st.text_area("Your taste:", "I love sci-fi and AI.", height=100)

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Ask:", "Recommend a movie")
with col2:
    st.write("")
    st.write("")
    btn = st.button("Get Recommendations", type="primary")

if btn:
    with st.spinner("Thinking..."):
        result = get_recommendations(profile, query)
    if result.get("recommendations"):
        st.success("Top picks:")
        for r in result["recommendations"]:
            with st.expander(f"**{r['title']}** — {r.get('score', 0):.2f}"):
                st.write(r.get("reason", ""))
    else:
        st.error(result.get("reason", "Error"))
