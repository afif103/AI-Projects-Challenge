# utils/report.py
from fpdf import FPDF
from datetime import datetime
import textwrap
import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Replace problematic Unicode characters
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "…": "...", "•": "-",
        "→": "->", "\xa0": " ", "•": "-", "‒": "-"
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Remove any remaining non-ASCII characters
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    return text


def safe_multicell(pdf, text: str, width: float = 0, line_height: float = 6):
    """
    Custom MultiCell that safely wraps even long URLs or tokens.
    """
    text = clean_text(text)
    # break long unbroken strings
    wrapped_lines = []
    for word in text.split():
        if len(word) > 80:  # wrap very long URLs or tokens
            wrapped_lines.extend(textwrap.wrap(word, 80))
        else:
            wrapped_lines.append(word)
    text = " ".join(wrapped_lines)

    # Now split again by paragraphs and safely print
    for paragraph in text.split("\n"):
        lines = textwrap.wrap(paragraph, width=90)
        for line in lines:
            pdf.cell(0, line_height, line, ln=True)
        pdf.ln(1)


class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "AI News Digest", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} | {datetime.now():%Y-%m-%d %H:%M}", align="C")

    def add_summary(self, article_text: str, summary: str, key_points: list):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Original Article:", ln=True)
        self.set_font("Helvetica", "", 10)
        safe_multicell(self, article_text[:2000] + ("..." if len(article_text) > 2000 else ""))
        self.ln(8)

        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "AI Summary:", ln=True)
        self.set_font("Helvetica", "", 10)
        safe_multicell(self, summary)
        self.ln(8)

        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Key Points:", ln=True)
        self.set_font("Helvetica", "", 10)
        for point in key_points:
            safe_multicell(self, f"- {point}")
        self.ln(10)


def generate_pdf(title: str, article_text: str, summary: str, key_points: list, filename: str):
    pdf = PDFReport()
    pdf.add_page()
    pdf.add_summary(article_text, summary, key_points)
    pdf.output(filename)
