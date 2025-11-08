# backend/db/vector_store.py
import warnings
warnings.filterwarnings("ignore")

from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma

# Direct embedding model
embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")

class SentenceTransformerEmbeddings:
    def embed_documents(self, texts):
        return embeddings_model.encode(texts).tolist()
    
    def embed_query(self, text):
        return embeddings_model.encode([text]).tolist()[0]

embeddings = SentenceTransformerEmbeddings()

def get_vector_store():
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )