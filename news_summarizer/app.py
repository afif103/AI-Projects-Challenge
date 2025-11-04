# app.py
import streamlit as st
import torch
from backend.loader import load_from_text, load_from_url
from backend.llm import get_llm, get_prompt_template, summarize_text
from utils.report import generate_pdf
from datetime import datetime

# === Page Config ===
st.set_page_config(page_title="News Summarizer", page_icon="📰", layout="centered")

# === Sidebar Badges ===
with st.sidebar:
    st.markdown("### 🏆 GPU ACCELERATED • 🔒 Local • 💸 Free")
    st.markdown("---")
    st.caption("Built by [Rami Afif](https://linkedin.com/in/ramiafif)")
    st.caption("Zero token cost • Fully offline-capable")

# === Header ===
st.title("📰 News Summarizer")
st.markdown("*Paste article or URL → Get clean, neutral summary + PDF report*")

# === Input Mode ===
input_mode = st.radio("Input Method", ["Paste Text", "Enter URL"], horizontal=True)

article_text = ""
if input_mode == "Paste Text":
    article_text = st.text_area("Paste news article:", height=300, max_chars=5000)
else:
    url = st.text_input("Enter article URL:")
    if url:
        with st.spinner("Scraping article..."):
            try:
                article_text = load_from_url(url)
                st.success("Article loaded!")
            except Exception as e:
                st.error(str(e))

if article_text:
    st.markdown("### 📄 Preview")
    st.text_area("Cleaned Article", article_text[:1000] + ("..." if len(article_text) > 1000 else ""), height=150, disabled=True)

    if st.button("🚀 Generate Summary", type="primary"):
        with st.spinner("Summarizing with Llama 3.2..."):
            try:
                llm = get_llm()
                prompt = get_prompt_template()
                summary = summarize_text(llm, prompt, article_text)

                # Extract key points (simple heuristic)
                sentences = [s.strip() for s in summary.split('.') if s.strip() and '?' not in s]
                key_points = sentences[:3] if len(sentences) >= 3 else sentences

                st.success("Summary Generated!")
                st.markdown("### 📋 Summary")
                st.write(summary)

                st.markdown("### 🔑 Key Points")
                for point in key_points:
                    st.markdown(f"• {point}")

                # PDF Report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_file = f"summary_{timestamp}.pdf"
                generate_pdf("AI News Digest", summary, key_points, pdf_file)

                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Download PDF Report", f, file_name=pdf_file, mime="application/pdf")

            except Exception as e:
                st.error(f"Summarization failed: {str(e)}")
                st.info("💡 Tip: Run `ollama serve` in terminal if using locally.")

# === Footer ===
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**GPU Detected:** " + ("✅ Yes" if torch.cuda.is_available() else "❌ No (CPU mode)"))
with col2:
    st.markdown("**Ollama Status:** " + ("✅ Running" if 'llm' in locals() else "⚠️ Start `ollama serve`"))

st.caption("© 2025 Rami Afif • LLMOps Engineer")