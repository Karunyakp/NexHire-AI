from fpdf import FPDF
import os
import re

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
        
       
        return text.encode('latin-1', 'replace').decode('latin-1')


    def render_table_row(pdf, cells, widths, header=False):
        max_h = 0
        # Calculate max height for the row
        for i, cell in enumerate(cells):
            if i < len(widths):
                # Calculate height needed for this cell
                lines = pdf.multi_cell(widths[i], 6, str(cell).strip(), split_only=True)
                h = len(lines) * 6
                if h > max_h: max_h = h
        
    
        if max_h == 0: max_h = 6

     
        if pdf.get_y() + max_h > 270:
            pdf.add_page()

      
        x = pdf.get_x()
        y = pdf.get_y()
        for i, cell in enumerate(cells):
            if i < len(widths):
                if header:
                    pdf.set_font("Arial", 'B', 10)
                    pdf.set_fill_color(230, 230, 230)
                else:
                    pdf.set_font("Arial", size=10)
                    pdf.set_fill_color(255, 255, 255)
               
                pdf.rect(x, y, widths[i], max_h, 'DF')
               
                pdf.multi_cell(widths[i], 6, str(cell).strip(), align='L')
             
                x += widths[i]
                pdf.set_xy(x, y)
        
        pdf.ln(max_h)

  
    def render_content(pdf, text):
        lines = text.split('\n')
        in_table = False
        table_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if not in_table: pdf.ln(2)
                continue

           
            if line.startswith('|') and '|' in line[1:]:
                in_table = True
                table_lines.append(line)
            else:
                # If we were in a table and hit a non-table line, render the table now
                if in_table:
                    # Render the accumulated table
                    process_markdown_table(pdf, table_lines)
                    table_lines = []
                    in_table = False

                if line.startswith('##'):
                    pdf.ln(5)
                    pdf.set_font("Arial", 'B', 14)
                    pdf.multi_cell(0, 8, line.replace('#', '').strip())
                elif line.startswith('**') or line.startswith('###'):
                    pdf.ln(2)
                    pdf.set_font("Arial", 'B', 11)
                    clean_line = line.replace('*', '').replace('#', '').strip()
                    pdf.multi_cell(0, 6, clean_line)
                else:
                    pdf.set_font("Arial", size=11)
                    # Handle bolding inside text roughly (removing markers)
                    pdf.multi_cell(0, 6, line.replace('**', ''))

        if in_table:
            process_markdown_table(pdf, table_lines)

    def process_markdown_table(pdf, table_lines):
        if len(table_lines) < 2: return
        
       
        rows = []
        for line in table_lines:
           
            cells = [c.strip() for c in line.strip('|').split('|')]
            rows.append(cells)
     
        data_rows = []
        for r in rows:
            if not r: continue
            # Check if row looks like separator line (---)
            if not all(c.replace('-', '').replace(':', '').strip() == '' for c in r):
                data_rows.append(r)
        
        if not data_rows: return


        num_cols = len(data_rows[0])
        if num_cols == 0: return
        
        col_width = 190 / num_cols
        widths = [col_width] * num_cols
        
       
        render_table_row(pdf, data_rows[0], widths, header=True)
   
        for row in data_rows[1:]:
            # Ensure row has same number of columns, pad if needed
            while len(row) < num_cols:
                row.append("")
            render_table_row(pdf, row, widths, header=False)
        
        pdf.ln(5)

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    username = sanitize_text(username)
    role = sanitize_text(role)
    category = sanitize_text(category)
    feedback = sanitize_text(feedback)
    resume_skills = sanitize_text(resume_skills)
    missing_skills = sanitize_text(missing_skills)
    

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Candidate Evaluation Report", 0, 1, 'L')
    pdf.line(10, 35, 200, 35)
    pdf.ln(5)

  
    pdf.set_font("Arial", size=11)
    
    def create_row(label, value):
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, label, 0, 0)
        pdf.set_font("Arial", size=11)
        # Ensure value fits nicely
        pdf.multi_cell(0, 8, value, 0, 'L')

    create_row("Candidate Name:", username)
    create_row("Target Role:", role)
    create_row("Profile Category:", category)
    
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 12, f" Overall Match Score: {score}%", 0, 1, 'C', fill=True)
    pdf.ln(5)

 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Skills Breakdown", 0, 1)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(95, 8, "Matched Skills", 1, 0, 'C', fill=True)
    pdf.cell(95, 8, "Missing / Gap Skills", 1, 1, 'C', fill=True)

    pdf.set_font("Arial", size=10)
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    pdf.multi_cell(95, 6, resume_skills, border=1, align='L')
    h1 = pdf.get_y() - y_start
    
    pdf.set_xy(x_start + 95, y_start)
    pdf.multi_cell(95, 6, missing_skills, border=1, align='L')
    h2 = pdf.get_y() - y_start
    
    pdf.set_y(y_start + max(h1, h2) + 5)

  
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detailed Analysis & Roadmap", 0, 1)
    

    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 6, "Note: Refer to the NexHire App for interactive learning resources and detailed plan tracking.")
    pdf.ln(2)
    

    render_content(pdf, feedback)
    
    return pdf.output(dest='S').encode('latin-1')

