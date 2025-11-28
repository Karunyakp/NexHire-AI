import google.generativeai as genai
import streamlit as st

# --- API CONFIGURATION ---
# Try to get the key from Streamlit Secrets (Cloud)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback for local testing (Keep your real key here if testing locally)
    API_KEY = "PASTE_YOUR_KEY_HERE"

# Configure the AI
if API_KEY != "PASTE_YOUR_KEY_HERE":
    genai.configure(api_key=API_KEY)
    # SWITCHING TO THE STABLE MODEL "gemini-pro"
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# --- FUNCTION 1: GET MATCH SCORE ---
def get_ats_score(resume_text, job_desc):
    if not model: return 0
    
    # Prompt optimized for Gemini Pro
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
        # Extract number
        return int(''.join(filter(str.isdigit, response.text)))
    except Exception as e:
        # If AI fails, return a safe default to prevent crashing
        return 0

# --- FUNCTION 2: GET FEEDBACK ---
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