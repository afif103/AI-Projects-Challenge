# app.py
import streamlit as st
import torch
import os
from backend.loader import load_from_text, load_from_url
from backend.llm import get_llm, get_prompt_template, summarize_text
from utils.report import generate_pdf
from datetime import datetime

# === PAGE CONFIG ===
st.set_page_config(
    page_title="News Summarizer",
    page_icon="Newspaper",
    layout="centered"
)

# === CLOUD DETECTION ===
IS_CLOUD = not os.getenv('OLLAMA_HOST', False) and not torch.cuda.is_available()

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### GPU ACCELERATED • Local • Private • Free")
    st.markdown("---")
    st.caption("By [Rami Afif](https://linkedin.com/in/ramiafif)")
    st.caption("Zero token cost • Fully offline-capable")

# === HEADER ===
st.title("Newspaper News Summarizer")
st.markdown("*Paste article or URL → Get clean, neutral summary + PDF report*")

# === INPUT MODE ===
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
                st.error(f"Scraping failed: {str(e)}")

# === PREVIEW ===
if article_text:
    st.markdown("### Preview")
    preview = article_text[:1000] + ("..." if len(article_text) > 1000 else "")
    st.text_area("Cleaned Article", preview, height=150, disabled=True)

    # === GENERATE SUMMARY ===
    if st.button("Generate Summary", type="primary"):
        with st.spinner("Processing..."):
            try:
                # === CLOUD FALLBACK ===
                if IS_CLOUD:
                    st.warning("Cloud Mode: LLM disabled (no Ollama). Use local GPU for full AI summaries!")
                    summary = (
                        "This is a demo on Streamlit Cloud. "
                        "Paste this article into your local version to get a full AI summary with Llama 3.2."
                    )
                    key_points = [
                        "Cloud mode: UI + PDF only",
                        "Local mode: Full AI summary with Ollama",
                        "Run locally with `ollama serve`"
                    ]

                # === LOCAL AI MODE ===
                else:
                    llm = get_llm()
                    prompt = get_prompt_template()
                    summary = summarize_text(llm, prompt, article_text)

                    # Extract key points
                    key_points = []
                    for line in summary.split('\n'):
                        line = line.strip()
                        if line and len(line) > 20:
                            line = line.lstrip('•*- ').split('.', 1)[0].strip()
                            if line:
                                key_points.append(line)
                    key_points = key_points[:3]

                # === DISPLAY RESULTS ===
                st.success("Done!")
                st.markdown("### Summary")
                st.write(summary)

                st.markdown("### Key Points")
                for point in key_points:
                    st.markdown(f"- {point}")

                # === PDF REPORT ===
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_file = f"summary_{timestamp}.pdf"
                generate_pdf("AI News Digest", summary, key_points, pdf_file)

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "Download PDF Report",
                        f,
                        file_name=pdf_file,
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Tip: Run `ollama serve` locally if using GPU mode.")

# === FOOTER ===
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**GPU:** {'Yes' if torch.cuda.is_available() else 'No'}")
with col2:
    st.markdown(f"**Ollama:** {'Running' if not IS_CLOUD else 'Cloud (Disabled)'}")

st.caption("© 2025 Rami Afif • LLMOps Engineer")
