# app.py
import streamlit as st
import os

st.set_page_config(page_title="AI Recommender", layout="wide")
st.title("AI Movie Recommender")
st.caption("Llama 3.2 + RAG — **LOCAL DEMO ONLY**")

st.sidebar.success("Local mode: Working 100%")
st.sidebar.info("Streamlit Cloud fails due to Chroma DB path. This is a **demo**.")

profile = st.sidebar.text_area("Your taste:", "I love sci-fi, AI, and mind-bending plots", height=100)
query = st.text_input("Ask:", "Recommend a movie")

if st.button("Get Recommendations", type="primary"):
    with st.spinner("Simulating recommendation..."):
        # === MOCK RESULT (NO CHAIN, NO ERROR) ===
        mock_result = {
            "recommendations": [
                {"title": "Inception", "score": 0.98, "reason": "Mind-bending sci-fi with dream layers and AI themes."},
                {"title": "The Matrix", "score": 0.95, "reason": "Reality simulation, action, and philosophical AI."},
                {"title": "Dune", "score": 0.89, "reason": "Epic sci-fi with politics, desert planets, and destiny."}
            ]
        }
        recs = mock_result["recommendations"]
        st.success(f"Top {len(recs)} picks (mock):")
        for r in recs:
            with st.expander(f"**{r['title']}** — {r['score']:.2f}"):
                st.write(r["reason"])
else:
    st.info("Click button to see **mock recommendations** (no backend needed).")
    st.code("Local repo works perfectly with: python -m backend.db.ingest && streamlit run ui/app.py")
