# backend/matcher.py
# Computes match score and skill gaps using embeddings
from sklearn.metrics.pairwise import cosine_similarity
from utils.skills import extract_skills
import numpy as np

def compute_match_score(resume_text: str, job_desc: str, embeddings):
    """
    Uses cosine similarity between resume and job description embeddings.
    Returns percentage (0–100).
    """
    resume_vec = embeddings.embed_query(resume_text)
    jd_vec = embeddings.embed_query(job_desc)
    sim = cosine_similarity([resume_vec], [jd_vec])[0][0]
    return int(sim * 100)

def get_missing_skills(resume_text: str, job_desc: str):
    """
    Compares extracted skills from both texts.
    Returns: missing, resume_skills, jd_skills
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_desc)
    missing = [s for s in jd_skills if s not in resume_skills]
    return missing, resume_skills, jd_skills