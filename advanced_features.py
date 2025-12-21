from fpdf import FPDF

def generate_pdf_report(username, role, score, feedback, resume_skills, missing_skills, category):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'NexHire Platinum Analysis Report', 0, 1, 'C')
            self.ln(5)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, 'Developed by Karunya K. P.', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt=f"Candidate: {username}", ln=True)
    pdf.cell(200, 8, txt=f"Target Role: {role}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=24)
    pdf.cell(200, 20, txt=f"ATS Match Score: {score}%", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=feedback.replace("*", ""))
    return pdf.output(dest='S').encode('latin-1')
