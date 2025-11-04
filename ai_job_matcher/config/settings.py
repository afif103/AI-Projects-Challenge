# config/settings.py
# Central configuration file for input/output limits and safe defaults
# PRIORITY: ONLINE FIRST → LOCAL FALLBACK (for best accuracy + privacy)

# === INPUT VALIDATION & LIMITS ===
MAX_RESUME_PAGES = 5                    # Limit PDF pages to prevent overload
MIN_TEXT_LENGTH = 200                   # Minimum chars to consider valid resume
MAX_TEXT_LENGTH = 8000                  # Max chars to process (avoid OOM)
MAX_SUGGESTION_TOKENS = 150             # Limit LLM output length

# === MODE PRIORITY ===
PREFER_ONLINE = True                    # Set False for local-only (privacy mode)

# === EMBEDDING MODELS ===
ONLINE_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Stronger, 768-dim
LOCAL_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"    # Fast, 384-dim

# === LLM MODELS ===
ONLINE_LLM_MODEL = "google/flan-t5-large"   # Better coherence, online
LOCAL_LLM_MODEL = "llama3.2"                # Private, runs locally via Ollama

# === VECTOR DB ===
VECTOR_DB = "pinecone" if PREFER_ONLINE else "faiss"
# "pinecone" = cloud, scalable | "faiss" = local, fast, private

# === SAFE SKILLS (Prevents hallucinations, bias, or fake skills) ===
SAFE_SKILLS = [
    "Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker", "SQL",
    "Machine Learning", "TensorFlow", "Git", "Agile", "Scrum", "Kubernetes",
    "Pandas", "Django", "Flask", "FastAPI", "MongoDB", "PostgreSQL", "Linux",
    "HTML", "CSS", "TypeScript", "CI/CD", "Terraform", "GraphQL", "REST API"
]