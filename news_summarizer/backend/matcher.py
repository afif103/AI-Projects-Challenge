# backend/matcher.py
from langchain_community.vectorstores import FAISS
from backend.embedder import get_embeddings
from config.settings import FAISS_INDEX_PATH
from langchain_text_splitters import RecursiveCharacterTextSplitter

def build_vector_store(documents):
    embeddings = get_embeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    vectorstore = FAISS.from_documents(splits, embeddings)
    FAISS_INDEX_PATH.mkdir(exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)
    return vectorstore