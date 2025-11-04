# backend/llm.py
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from config.settings import LLM_MODEL, MAX_OUTPUT_CHARS

def get_llm():
    try:
        return Ollama(model=LLM_MODEL, temperature=0.3)
    except Exception as e:
        raise RuntimeError(f"Ollama not available. Is it running? Error: {e}")

def get_prompt_template():
    return PromptTemplate.from_template(
        "You are a neutral AI news summarizer. Summarize in 3–5 sentences. "
        "Be factual, professional, no opinions. Never use harmful language.\n\n"
        "Article: {text}\n\nSummary:"
    )

def summarize_text(llm, prompt, text: str) -> str:
    chain = prompt | llm
    try:
        result = chain.invoke({"text": text})
        return result[:MAX_OUTPUT_CHARS].strip()
    except Exception as e:
        return f"[Error generating summary: {str(e)}]"