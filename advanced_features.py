import json
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# ============ SKILL EXTRACTION ============
def extract_skills(text):
    """Extract common technical skills from resume/job description"""
    common_skills = {
        'Python', 'JavaScript', 'Java', 'C++', 'C#', 'TypeScript', 'Ruby', 'PHP',
        'React', 'Vue', 'Angular', 'Django', 'Flask', 'FastAPI', 'Node.js',
        'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Firebase',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git',
        'REST API', 'GraphQL', 'Microservices', 'CI/CD', 'DevOps',
        'Machine Learning', 'TensorFlow', 'PyTorch', 'NLP', 'Computer Vision',
        'HTML', 'CSS', 'SASS', 'Bootstrap', 'Tailwind',
        'Agile', 'Scrum', 'Jira', 'Slack', 'Figma', 'Adobe XD'
    }
    
    found_skills = []
    for skill in common_skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)
    return list(set(found_skills))

# ============ ANALYTICS ============
def calculate_score_stats(scores):
    """Calculate statistics from score list"""
    if not scores:
        return {"avg": 0, "median": 0, "max": 0, "min": 0}
    
    import statistics
    return {
        "avg": round(statistics.mean(scores), 1),
        "median": statistics.median(scores),
        "max": max(scores),
        "min": min(scores)
    }

def get_score_distribution(scores):
    """Categorize scores into ranges"""
    distribution = {
        "Excellent (70+)": len([s for s in scores if s >= 70]),
        "Good (50-69)": len([s for s in scores if 50 <= s < 70]),
        "Needs Work (<50)": len([s for s in scores if s < 50])
    }
    return distribution

def get_trend_data(history):
    """Get score trend over time for chart"""
    if not history:
        return [], []
    
    dates = [row[3] for row in history]  # Assuming date is 4th column
    scores = [row[2] for row in history]  # Assuming score is 3rd column
    return dates, scores

# ============ REPORT GENERATION ============
def generate_pdf_report(username, job_role, score, feedback, resume_skills, job_skills):
    """Generate PDF report of analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"NexHire Analysis - {job_role}")
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366F1'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    story = []
    
    # Header
    story.append(Paragraph("NexHire Resume Analysis Report", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Analysis Details
    details = [
        ["Candidate", username.title()],
        ["Position", job_role or "Not specified"],
        ["Analysis Date", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Match Score", f"{score}%"]
    ]
    
    details_table = Table(details, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Skills Section
    story.append(Paragraph("Skills Analysis", heading_style))
    
    skills_data = [["Matched Skills", "Missing Skills"]]
    matched = [s for s in resume_skills if s in job_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    
    matched_text = ", ".join(matched[:10]) + ("..." if len(matched) > 10 else "")
    missing_text = ", ".join(missing[:10]) + ("..." if len(missing) > 10 else "")
    
    skills_data.append([matched_text or "None", missing_text or "None"])
    
    skills_table = Table(skills_data, colWidths=[3.5*inch, 3.5*inch])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 0.3*inch))
    
    # AI Feedback
    story.append(Paragraph("AI Assessment", heading_style))
    feedback_para = Paragraph(feedback.replace('\n', '<br/>'), styles['Normal'])
    story.append(feedback_para)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("© 2025 NexHire. Confidential.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_csv_report(history):
    """Generate CSV from scan history"""
    df = pd.DataFrame(history, columns=['Username', 'Job Role', 'Score', 'Date'])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

# ============ ADMIN ANALYTICS ============
def get_platform_stats(all_history):
    """Get platform-wide statistics"""
    if not all_history:
        return {}
    
    scores = [row[2] for row in all_history]
    return {
        "total_scans": len(all_history),
        "avg_score": round(sum(scores) / len(scores), 1),
        "unique_users": len(set([row[0] for row in all_history])),
        "best_score": max(scores),
        "worst_score": min(scores)
    }

def get_top_positions(all_history):
    """Get most analyzed positions"""
    roles = {}
    for row in all_history:
        role = row[1] or "Not specified"
        roles[role] = roles.get(role, 0) + 1
    
    return sorted(roles.items(), key=lambda x: x[1], reverse=True)[:10]

def get_user_stats(username, history):
    """Get individual user statistics"""
    if not history:
        return {}
    
    scores = [row[2] for row in history]
    return {
        "total_scans": len(history),
        "avg_score": round(sum(scores) / len(scores), 1),
        "best_score": max(scores),
        "last_scan": history[0][3] if history else "Never"
    }
