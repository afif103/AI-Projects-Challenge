# utils/skills.py
# Extracts only pre-approved skills to avoid hallucinations or fake terms
import re
from config.settings import SAFE_SKILLS

def extract_skills(text: str):
    """
    Case-insensitive exact word match for known safe skills.
    Prevents LLM from inventing skills like "Quantum Hacking".
    """
    found = []
    for skill in SAFE_SKILLS:
        # Use word boundaries \b to avoid partial matches (e.g., "Java" in "JavaScript")
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found.append(skill)
    return list(set(found))  # Remove duplicates