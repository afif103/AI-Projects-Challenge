# app.py
# Streamlit frontend – clean, user-friendly, and secure
import streamlit as st
from backend.loader import load_resume_pdf
from backend.embedder import get_embeddings
from backend.matcher import compute_match_score, get_missing_skills
from backend.suggester import generate_suggestions
from utils.report import generate_pdf_report
from config.settings import PREFER_ONLINE, ONLINE_LLM_MODEL, LOCAL_LLM_MODEL
import base64


# === PAGE CONFIG ===
st.set_page_config(
    page_title="AI Job Matcher",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AI Job Matcher")

mode = "Online-First (Best Accuracy)" if PREFER_ONLINE else "Local-Only (Private)"
st.caption(f"Local • Private • Free | **{mode}** | LangChain + Ollama + FAISS")

# === INPUT SECTION ===
col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader(
        "Upload Resume (PDF)",
        type="pdf",
        help="Max 5 pages, detailed content recommended"
    )

with col2:
    job_desc = st.text_area(
        "Paste Job Description",
        height=200,
        placeholder="e.g., Seeking Python developer with AWS and Docker experience..."
    )

# === ANALYSIS LOGIC ===
if resume_file and job_desc:
    if len(job_desc) < 50:
        st.error("Job description too short. Please paste a full JD.")
    else:
        try:
            # === SPINNER WITH MODE INFO ===
            mode_text = "online-first (best accuracy)" if PREFER_ONLINE else "local-only (private)"
            with st.spinner(f"Analyzing in **{mode_text}** mode..."):
                
                # Step 1: Load and validate resume
                resume_text = load_resume_pdf(resume_file)

                # Step 2: Get embeddings (online-first)
                embeddings = get_embeddings()  # ← No mode param — handled in backend
                if hasattr(embeddings, 'model_kwargs') and embeddings.model_kwargs.get('device') == 'cuda':
                     st.success("GPU ACCELERATED (Online Model)")
                else:
                    st.info("Using local CPU (Private)")

                # Step 3: Compute match score
                score = compute_match_score(resume_text, job_desc, embeddings)

                # Step 4: Extract skills and find gaps
                missing, resume_skills, jd_skills = get_missing_skills(resume_text, job_desc)

                # Step 5: Generate safe suggestions
                suggestion = generate_suggestions(resume_text, jd_skills)

            # === DISPLAY RESULTS ===
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Match Score", f"{score}%", delta=f"{score-50:+}% vs average")
            c2.metric("Skills Found", len(resume_skills))
            c3.metric("Missing Skills", len(missing))

            if "cuda" in str(embeddings):
                st.success("GPU ACCELERATED • Online Model")
            else:
                st.info("Local CPU • Private Mode")

            # Missing Skills Alert
            if missing:
                st.warning("Missing Skills: " + ", ".join(missing))
            else:
                st.success("All required skills detected!")

            # === UI FEEDBACK: ONLINE vs LOCAL ===
            if PREFER_ONLINE:
                # Try to detect if online LLM was used (by checking model in suggestion)
                if any(model in suggestion.lower() for model in ["flan", "t5", "huggingface"]):
                    st.success("Suggestions powered by **online LLM** (high accuracy)")
                else:
                    st.info("Online LLM unavailable → used **local LLM** (private)")
            else:
                st.info("Suggestions powered by **local LLM** (private mode)")

            # Suggestions
            st.subheader("Suggested Resume Edits")
            st.info(suggestion)

            # PDF Report Download
            report_data = {
                "score": score,
                "missing": missing,
                "suggestions": suggestion
            }
            b64 = generate_pdf_report(report_data)
            href = f'<a href="data:application/pdf;base64,{b64}" download="AI_Job_Matcher_Report.pdf">Download Full Report (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Debug: Show truncated resume
            with st.expander("View Resume Text (truncated)"):
                st.text(resume_text[:1500] + ("..." if len(resume_text) > 1500 else ""))

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.info("Try a different PDF or shorter job description.")
            

else:
    st.info("Upload your **resume PDF** and **paste the job description** to begin.")
    st.markdown(
        "### How it works:\n"
        "1. Upload resume\n"
        "2. Paste job description\n"
        "3. Get match score + suggestions\n"
        f"**Current Mode:** {'Online-First (Best Accuracy)' if PREFER_ONLINE else 'Local-Only (Private)'}"
    )