# utils/report.py
from fpdf import FPDF
import base64
from datetime import datetime
import os

def generate_pdf_report(data: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # === LOAD REGULAR + BOLD FONTS ===
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)  # ← ADD THIS LINE

    # Title (Bold)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 10, "AI Job Matcher Report", ln=1, align="C")
    pdf.set_font("DejaVu", size=10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align="C")
    pdf.ln(10)

    # Match Score (Bold)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, f"Match Score: {data['score']}%", ln=1)
    pdf.set_font("DejaVu", size=11)
    pdf.cell(0, 8, f"Your resume matches {data['score']}% of the job.", ln=1)
    pdf.ln(5)

    # Missing Skills (Bold)
    pdf.set_font("DejaVu", "B", 12)
    missing = data['missing']
    pdf.cell(0, 10, f"Missing Skills: {', '.join(missing) if missing else 'None'}", ln=1)
    if missing:
        pdf.cell(0, 8, "Add these skills to improve your match.", ln=1)
    else:
        pdf.cell(0, 8, "All key skills found!", ln=1)
    pdf.ln(5)

    # Suggestions (Bold)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Suggested Resume Edits:", ln=1)
    pdf.set_font("DejaVu", size=11)
    for line in data['suggestions'].split('\n'):
        if line.strip():
            clean_line = line.replace('•', '-')
            pdf.multi_cell(0, 7, clean_line)

    # Footer
    pdf.set_font("DejaVu", size=8)
    pdf.cell(0, 10, "Local • Private • Free | GPU Accelerated | LangChain + Ollama", ln=1, align="C")

    # Save
    pdf_file = "job_matcher_report.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return b64

    