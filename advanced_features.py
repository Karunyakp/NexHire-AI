from fpdf import FPDF
import os

def generate_pdf_report(username, role, score, feedback, resume_skills, missing_skills, category):
    class PDF(FPDF):
        def header(self):
            # Logo
            if os.path.exists('logo.png'):
                try:
                    self.image('logo.png', 10, 8, 25)
                except:
                    pass
            
            self.set_font('Arial', 'B', 15)
            # Move to the right to not overlap with logo
            self.cell(30)
            self.cell(0, 10, 'NexHire Analysis Report', 0, 1, 'C')
            self.ln(20) # Add a line break after header

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, 'Developed by Karunya K. P. | NexHire Inc.', 0, 0, 'C')

    def sanitize_text(text):
        """Replaces incompatible unicode characters with ASCII equivalents."""
        if not text: return ""
        text = str(text)
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '-',  # Dashes
            '\u2022': '*',                 # Bullet points
            '\u2026': '...',               # Ellipsis
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Remove any remaining non-latin-1 characters
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Sanitize all inputs
    username = sanitize_text(username)
    role = sanitize_text(role)
    category = sanitize_text(category)
    feedback = sanitize_text(feedback)
    resume_skills = sanitize_text(resume_skills)
    missing_skills = sanitize_text(missing_skills)
    
    # --- REPORT TITLE SECTION ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Candidate Evaluation", 0, 1, 'L')
    pdf.line(10, 35, 200, 35) # Draw a line under title
    pdf.ln(5)

    # --- INFO TABLE ---
    pdf.set_font("Arial", size=11)
    
    # Function to create a row
    def create_row(label, value):
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, label, 0, 0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, value, 0, 1)

    create_row("Candidate Name:", username)
    create_row("Target Role:", role)
    create_row("Profile Category:", category)
    
    pdf.ln(5)
    
    # --- SCORE SECTION ---
    pdf.set_fill_color(240, 240, 240) # Light gray background
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, f" Overall Match Score: {score}%", 0, 1, 'C', fill=True)
    pdf.ln(5)

    # --- SKILLS TABLE ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Skills Breakdown", 0, 1)
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(95, 8, "Matched Skills (Present)", 1, 0, 'C', fill=True)
    pdf.cell(95, 8, "Missing / Gap Skills", 1, 1, 'C', fill=True)
    
    # Table Content
    pdf.set_font("Arial", size=10)
    
    # Calculate height needed
    # A simple approach: print text in multi_cell side by side
    # We save current position
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    # Cell 1: Matched Skills
    pdf.multi_cell(95, 6, resume_skills, border=1, align='L')
    
    # Get the height of the first cell
    height1 = pdf.get_y() - y_start
    
    # Reset position to right of first cell
    pdf.set_xy(x_start + 95, y_start)
    
    # Cell 2: Missing Skills
    pdf.multi_cell(95, 6, missing_skills, border=1, align='L')
    
    # Get height of second cell
    height2 = pdf.get_y() - y_start
    
    # Set Y to the max height to continue below the table
    pdf.set_y(y_start + max(height1, height2) + 5)

    # --- FEEDBACK & ROADMAP SECTION ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detailed Analysis & Roadmap", 0, 1)
    
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, txt=feedback)
    
    return pdf.output(dest='S').encode('latin-1')
