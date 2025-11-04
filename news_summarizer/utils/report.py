# utils/report.py
from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'News Summary Report', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', align='C')

    def add_summary(self, title, summary, key_points):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 6, summary)
        self.ln(5)

        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 8, "Key Points:", ln=True)
        self.set_font('Helvetica', '', 10)
        for point in key_points:
            self.cell(0, 6, f"- {point}", ln=True)  # ← SAFE DASH
        self.ln(10)

def generate_pdf(title, summary, key_points, filename="summary_report.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.add_summary(title, summary, key_points)
    pdf.output(filename)