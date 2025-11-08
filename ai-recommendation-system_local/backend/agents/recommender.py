# backend/agents/recommender.py
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama
from backend.core.prompts import RECOMMENDER_PROMPT
from backend.db.vector_store import get_vector_store
import os

os.environ["LANGCHAIN_TRACING_V2"] = "false"

llm = ChatOllama(model="llama3.2:3b", temperature=0.3, timeout=60)

vector_store = get_vector_store()
retriever = vector_store.as_retriever(search_kwargs={"k": 10})

prompt = PromptTemplate.from_template(RECOMMENDER_PROMPT)
parser = JsonOutputParser()

def format_docs(docs):
    if not docs:
        return "No items in database."
    
    formatted = []
    for d in docs:
        try:
            title = d.metadata.get("title", "Unknown")
            content = d.page_content
            if isinstance(content, str):
                content = content.replace("\x00", "").strip()
            formatted.append(f"{title}: {content}")
        except:
            formatted.append("Parse error.")
    
    return "\n".join(formatted) if formatted else "No valid items."

chain = (
    {"context": retriever | format_docs, "profile": RunnablePassthrough(), "input": RunnablePassthrough()}
    | prompt
    | llm
    | parser
)

def get_recommendations(profile: str, query: str, history: list = None):
    try:
        response = chain.invoke({"input": query, "profile": profile})
        if not isinstance(response, dict):
            return {"recommendations": [], "reason": "Invalid JSON"}
        recs = response.get("recommendations", [])
        return {"recommendations": recs[:3]} if recs else {"recommendations": [], "reason": "No matches"}
    except Exception as e:
        return {"recommendations": [], "reason": f"Error: {str(e)}"}