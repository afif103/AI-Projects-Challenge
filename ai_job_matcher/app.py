# app.py
import streamlit as st
import torch
import os
from backend.loader import load_from_text, load_from_url, load_from_pdf_file
from backend.llm import get_llm, get_prompt_template, summarize_text
from utils.report import generate_pdf
from datetime import datetime
import time
import requests

st.set_page_config(page_title="News Summarizer", page_icon="Newspaper", layout="centered")


def is_ollama_available():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

IS_CLOUD = not is_ollama_available()


with st.sidebar:
    st.markdown("### GPU ACCELERATED • Local • Private • Free")
    st.markdown("---")
    st.caption("By [Rami Afif](https://linkedin.com/in/ramiafif)")
    st.caption("Zero token cost • Fully offline-capable")

st.title("Newspaper News Summarizer")
st.markdown("*Paste, URL, or PDF → AI summary + report*")

# === INPUT METHOD ===
input_mode = st.radio("Input", ["Paste Text", "Enter URL", "Upload PDF"], horizontal=True)

article_text = ""

if input_mode == "Paste Text":
    article_text = st.text_area("Paste article:", height=300, max_chars=5000)
    if article_text:
        article_text = load_from_text(article_text)

elif input_mode == "Enter URL":
    url = st.text_input("Article URL:")
    if url:
        with st.spinner("Scraping..."):
            try:
                article_text = load_from_url(url)
                st.success("Loaded!")
            except Exception as e:
                st.error(str(e))

elif input_mode == "Upload PDF":
    pdf_file = st.file_uploader("Upload PDF article", type="pdf")
    if pdf_file:
        with st.spinner("Extracting text from PDF..."):
            try:
                article_text = load_from_pdf_file(pdf_file)
                st.success("PDF loaded!")
            except Exception as e:
                st.error(str(e))

# === PREVIEW & GENERATE ===
if article_text:
    preview = article_text[:1000] + ("..." if len(article_text) > 1000 else "")
    st.markdown("### Preview")
    st.text_area("Cleaned Text", preview, height=150, disabled=True)

    if st.button("Generate Summary", type="primary"):
        with st.spinner("Summarizing with Llama 3.2..."):
            try:
                if IS_CLOUD:
                    st.warning("Cloud Mode: LLM disabled. Use local for AI.")
                    summary = "Demo mode. Run locally with Ollama for full AI."
                    key_points = ["Cloud: UI + PDF", "Local: Full AI", "Use `ollama serve`"]
                else:
                    llm = get_llm()
                    prompt = get_prompt_template()
                    summary = summarize_text(llm, prompt, article_text)
                    key_points = [s.strip().split('.')[0] for s in summary.split('\n') if s.strip() and len(s) > 20][:3]

                st.success("Done!")
                st.markdown("### Summary")
                st.write(summary)
                st.markdown("### Key Points")
                for p in key_points:
                    st.markdown(f"- {p}")

                # PDF Report
                pdf_path = f"summary_{datetime.now():%Y%m%d_%H%M%S}.pdf"
                try:
                    generate_pdf("AI News Digest", article_text, summary, key_points, pdf_path)
                    time.sleep(0.5)  # Let file write fully
                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download PDF Report",
                                f,
                                file_name=pdf_path,
                                mime="application/pdf"
                            )
                        st.success("PDF ready!")
                    else:
                         st.error("PDF generation failed — file too small.")
                except Exception as e:
                    st.error(f"PDF error: {e}")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Ensure Ollama Desktop is running and `llama3.2` is pulled.")

st.markdown("---")
st.caption("© 2025 Rami Afif • LLMOps Engineer")
