import google.generativeai as genai
import streamlit as st
import random

# --- KEY ROTATION LOGIC ---
def configure_model():
    """
    Picks a random API key from the list to distribute load
    """
    api_key = None
    try:
        # 1. Try to find a LIST of keys (Best for multiple users)
        if "GOOGLE_API_KEYS" in st.secrets:
            keys = st.secrets["GOOGLE_API_KEYS"]
            if isinstance(keys, list) and len(keys) > 0:
                api_key = random.choice(keys)
        
        # 2. Fallback to single key (Backward compatibility)
        if not api_key and "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]

    except Exception as e:
        st.error(f"Secret Error: {e}")
        return None

    if not api_key:
        st.error("❌ No Google API Keys found in Secrets.")
        return None
        
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error(f"❌ API Connection Error: {e}")
        return None

# --- CORE FUNCTIONS ---
def get_ats_score(resume_text, job_desc):
    model = configure_model()
    if not model: return 0
    
    prompt = f"""
    You are an ATS (Applicant Tracking System). Compare the Resume to the Job Description.
    Output ONLY a single integer from 0 to 100 representing the match percentage.
    Do not output any text, just the number.
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return int(''.join(filter(str.isdigit, response.text)))
    except:
        return 0

def get_feedback(resume_text, job_desc):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Act as a Senior Technical Recruiter. Provide detailed feedback.
    1. Strong Matches
    2. Missing Keywords
    3. Final Verdict (Hire/No Hire)
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating feedback."

# --- GENERATIVE SUITE ---
def generate_cover_letter(resume_text, job_desc):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Write a professional cover letter for this candidate.
    Highlight matching skills. Keep it under 300 words.
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating cover letter."

def generate_interview_questions(resume_text, job_desc):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Generate 5 targeted interview questions (3 Technical, 2 Behavioral) based on this candidate's gaps.
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating questions."

# --- STRATEGIC INSIGHTS ---
def get_market_analysis(resume_text, job_role):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Act as a Compensation Analyst. Based on the skills and experience in this resume for the role of '{job_role}':
    1. Estimate a competitive Salary Range (in USD and INR) for 2025.
    2. Rate the Market Demand for these skills (High/Medium/Low) with a brief reason.
    Output in clean markdown points.
    Resume: {resume_text[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error analyzing market."

def generate_email_draft(resume_text, job_role, email_type="Interview Invite"):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Write a professional email for a recruiter to send to this candidate.
    Type: {email_type}
    Job Role: {job_role}
    Context: Use specific details from their resume to make it personal.
    Resume: {resume_text[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating email."

def generate_learning_roadmap(resume_text, job_desc):
    model = configure_model()
    if not model: return "Error: Service Unavailable"
    
    prompt = f"""
    Identify the 3 biggest skill gaps between this Resume and Job Description.
    Create a "4-Week Learning Roadmap" to help the candidate learn these missing skills.
    Suggest specific topics to cover each week.
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating roadmap."
