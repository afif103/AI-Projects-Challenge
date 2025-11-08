# ingest.py
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import json, os

# Sample data
data = [
    {"title": "Inception", "description": "Dream heist with AI and sci-fi", "tags": {"genre": "sci-fi"}},
    {"title": "The Matrix", "description": "Reality is a simulation", "tags": {"genre": "sci-fi"}},
    {"title": "Dune", "description": "Epic desert planet adventure", "tags": {"genre": "sci-fi"}},
]

docs = [Document(page_content=f"{i['title']} - {i['description']}", metadata={"title": i["title"]}) for i in data]
Chroma.from_documents(docs, HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"), persist_directory="./chroma_db")
print("Indexed! Commit chroma_db/ to GitHub.")