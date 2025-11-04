# backend/suggester.py
from langchain_ollama import OllamaLLM
from langchain_community.llms import HuggingFaceHub
from utils.prompts import SUGGESTION_TEMPLATE
from langchain_core.prompts import PromptTemplate
import re
import os
from config.settings import PREFER_ONLINE, ONLINE_LLM_MODEL, LOCAL_LLM_MODEL

def get_llm():
    if PREFER_ONLINE:
        try:
            token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if token:
                return HuggingFaceHub(repo_id=ONLINE_LLM_MODEL, model_kwargs={"temperature": 0.3})
        except:
            pass

    try:
        if os.system("ollama list | grep -q llama3.2") == 0:
            return OllamaLLM(model=LOCAL_LLM_MODEL, temperature=0.3)
    except:
        pass

    return None

def generate_suggestions(resume_text: str, skills: list) -> str:
    try:
        llm = get_llm()
        if not llm:
            raise Exception()

        prompt = PromptTemplate.from_template(SUGGESTION_TEMPLATE)
        chain = prompt | llm
        result = chain.invoke({"resume_snippet": resume_text[:1000], "skills": ", ".join(skills)})

        suggestions = re.split(r'\d+\.', result)[1:4]
        suggestions = [s.strip() for s in suggestions if s.strip()][:3]

        defaults = [
            "Highlight projects with measurable impact.",
            "Use keywords from the job description.",
            "Quantify achievements with metrics."
        ]
        while len(suggestions) < 3:
            suggestions.append(defaults[len(suggestions)])

        return "\n".join([f"• {s}" for s in suggestions[:3]])

    except:
        return (
            "• Focus on job-relevant experience.\n"
            "• Add keywords from the job description.\n"
            "• Quantify your impact with numbers."
        )