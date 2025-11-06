# app.py — Streamlit + Groq Vision (Single File)
import streamlit as st
import base64
import io
import json
import os
from PIL import Image
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage  # Fixed import
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
MODEL = "llama-3.2-11b-vision-preview"
DEFAULT_LABELS = ["cat", "dog", "car", "tree", "person", "food", "house", "airplane"]
PROMPT = """Analyze the image and classify it as one of: {labels}.
Return JSON only:
{{
  "label": "your_answer",
  "confidence": 0.XX,
  "reason": "short explanation"
}}
"""

st.set_page_config(page_title="AI Image Classifier", page_icon="Camera", layout="wide")
st.title("Camera Zero-Shot Image Classifier")
st.caption("Powered by Groq + LLaVA-3.2 • Manila-built • Cloud Live")

# === LLM ===
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY missing in Streamlit Secrets")
        st.stop()
    return ChatGroq(model=MODEL, api_key=api_key, temperature=0.1, max_tokens=100)

llm = get_llm()

# === UI ===
with st.sidebar:
    st.header("Settings")
    labels_input = st.text_area("Labels (comma-separated)", ", ".join(DEFAULT_LABELS))
    labels = [l.strip() for l in labels_input.split(",") if l.strip()]
    label_str = ", ".join(labels)

st.subheader("Upload Image")
uploaded = st.file_uploader("JPG/PNG", type=["png", "jpg", "jpeg"])

if uploaded:
    image_bytes = uploaded.read()
    image = Image.open(io.BytesIO(image_bytes))
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image, caption="Input", use_container_width=True)

    with col2:
        st.subheader("Result")
        if st.button("Classify", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    # Resize & encode
                    buffered = io.BytesIO()
                    img = image.copy()
                    img.thumbnail((1024, 1024))
                    img.save(buffered, format="JPEG", quality=85)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()

                    # Build message
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": PROMPT.format(labels=label_str)},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]
                    )

                    # Call Groq
                    response = llm.invoke([message])
                    result = json.loads(response.content.strip())

                    # Display
                    st.json(result)
                    st.progress(result["confidence"])
                    st.markdown(f"**{result['label'].title()}** – {result['reason']}")
                    if result["confidence"] < 0.6:
                        st.warning("Low confidence")

                except json.JSONDecodeError:
                    st.error("Invalid JSON from model")
                except Exception as e:
                    st.error(f"Error: {e}")
