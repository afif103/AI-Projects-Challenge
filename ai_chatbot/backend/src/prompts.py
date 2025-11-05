# backend/src/prompts.py
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    """You are a helpful, concise AI assistant.

Context: {context}

User: {user_input}

Assistant: """
)