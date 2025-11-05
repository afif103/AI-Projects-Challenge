# backend/src/chains.py
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from .prompts import prompt_template
from .config import settings
import os

# Disable LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def create_chat_chain():
    llm = Ollama(
        model=settings.MODEL_NAME.split('/')[-1],  # "llama3.2:1b"
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.7
        # streaming=True REMOVED — not allowed in 0.3.1
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain