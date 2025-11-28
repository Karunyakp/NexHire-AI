import google.generativeai as genai
import streamlit as st

# --- API CONFIGURATION ---
try:
    # Attempt to load from Streamlit Secrets (Cloud)
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback for local testing
    API_KEY = "PASTE_YOUR_KEY_HERE"

if API_KEY != "PASTE_YOUR_KEY_HERE":
    genai.configure(api_key=API_KEY)
    # 🔴 FIX: Using 'gemini-pro' because it is 100% compatible with the Cloud
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

def get_ats_score(resume_text, job_desc):
    if not model: return 0
    
    prompt = f"""
    You are an ATS (Applicant Tracking System).
    Compare the Resume to the Job Description.
    Output ONLY a single integer from 0 to 100 representing the match percentage.
    Do not output any text, just the number.
    
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
    Act as a Senior Recruiter.
    Review this resume against the job description.
    Provide 3 bullet points on what is missing or needs improvement.
    Keep it professional and concise.
    
    Resume: {resume_text[:3000]}
    Job: {job_desc[:3000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"