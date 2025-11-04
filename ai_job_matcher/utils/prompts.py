# utils/prompts.py
# Reusable, safe prompt template to prevent harmful or off-topic output
from langchain_core.prompts import PromptTemplate

SUGGESTION_TEMPLATE = """You are a professional career coach. Improve this resume to match the job.

Resume:
{resume_snippet}

Required skills: {skills}

Provide exactly 3 short, professional bullet points to improve the resume. Focus on:
- Relevant experience
- Job keywords
- Quantified achievements

No harmful, biased, or unethical content. Do not suggest lying or exaggeration.

Suggestions:
1."""