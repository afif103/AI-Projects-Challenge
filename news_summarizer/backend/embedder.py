# backend/embedder.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL
import torch

def get_embeddings():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': device}
    )