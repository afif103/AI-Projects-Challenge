# vector_db/pinecone_index.py
# Optional: Use Pinecone for persistent, scalable vector search
from pinecone import Pinecone
import os

def get_pinecone_index():
    """
    Initializes Pinecone index (requires PINECONE_API_KEY in .streamlit/secrets.toml)
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not set")

    pc = Pinecone(api_key=api_key)
    index_name = "job-matcher"

    # Create index if not exists
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(index_name)