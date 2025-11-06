"""
Streamlit UI – All fixes applied
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import io  # ← Critical for BytesIO
from PIL import Image
from backend.classifier import ImageClassifier

st.set_page_config(page_title="Image Classifier", page_icon="Camera", layout="wide")
st.title("Camera Zero-Shot Image Classifier")
st.caption("Local (Ollama) • Cloud (Groq) • Manila-built")

# Sidebar
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox("Mode", ["ollama", "groq"])
    labels_input = st.text_area("Labels", "cat, dog, car, tree, person, food, house, airplane")
    labels = [l.strip() for l in labels_input.split(",") if l.strip()]

@st.cache_resource
def get_classifier(_mode, _labels):
    return ImageClassifier(mode=_mode, labels=_labels)

try:
    classifier = get_classifier(mode, labels)
    st.sidebar.success(f"Ready: {mode.upper()}")
except Exception as e:
    st.sidebar.error(f"Error: {e}")
    st.stop()

# Upload
st.subheader("Upload Image")
uploaded = st.file_uploader("JPG/PNG", type=["png", "jpg", "jpeg"])

if uploaded:
    image_bytes = uploaded.read()
    image = Image.open(io.BytesIO(image_bytes))  # ← Now works

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image, caption="Input", use_container_width=True)

    with col2:
        st.subheader("Result")
        if st.button("Classify", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    result = classifier.classify(image_bytes)
                    st.json(result)
                    st.progress(result["confidence"])
                    st.caption(f"Confidence: {result['confidence']:.1%}")
                    if result["confidence"] < 0.6:
                        st.warning("Low confidence")
                except Exception as e:
                    st.error(f"Classification failed: {e}")