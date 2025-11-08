# backend/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PINECONE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    return Settings()