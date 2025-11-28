import google.generativeai as genai
import streamlit as st
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
       API_KEY = ""

if API_KEY != "":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
def get_ats_score(resume_text, job_desc):
    if not model: return 0
    
    prompt = f"""
    Act as a strict ATS (Applicant Tracking System).
    Compare the Resume to the Job Description.
    Give a compatibility score (0-100).
    RETURN ONLY THE NUMBER. NO TEXT.
    
    Resume: {resume_text[:3000]}
    Job: {job_desc[:3000]}
    """
    try:
        response = model.generate_content(prompt)
        return int(''.join(filter(str.isdigit, response.text)))
    except:
        return 0
def get_feedback(resume_text, job_desc):
    if not model: return "Error: API Key Missing"
    
    prompt = f"""
    Act as a Senior Technical Recruiter.
    The candidate scored low on the ATS check.
    
    1. List 3 CRITICAL keywords missing from the resume.
    2. Suggest 1 project idea that would improve their odds for this specific job.
    
    Resume: {resume_text[:3000]}
    Job: {job_desc[:3000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"