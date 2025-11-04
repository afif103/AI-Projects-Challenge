# backend/embedder.py
from langchain_huggingface import HuggingFaceEmbeddings as HFOnline
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import PREFER_ONLINE, ONLINE_EMBEDDING_MODEL, LOCAL_EMBEDDING_MODEL
import torch
import streamlit as st

@st.cache_resource
def get_embeddings():
    if not PREFER_ONLINE:
        return HuggingFaceEmbeddings(model_name=LOCAL_EMBEDDING_MODEL)

    try:
        # === GPU DETECTED? USE IT! ===
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using **{device.upper()}** for online embeddings")

        return HFOnline(
            model_name=ONLINE_EMBEDDING_MODEL,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True}
        )
    except Exception as e:
        st.warning("Online GPU failed → using local CPU")
        print(f"[embedder] GPU error: {e}")
        return HuggingFaceEmbeddings(model_name=LOCAL_EMBEDDING_MODEL)