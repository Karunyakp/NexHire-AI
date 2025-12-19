import google.generativeai as genai
import streamlit as st

# --- API CONFIGURATION ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    API_KEY = None
    st.error("❌ GOOGLE_API_KEY not found in secrets. Add it to .streamlit/secrets.toml")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # Using the stable model
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error(f"❌ API Configuration Error: {e}")
        model = None
else:
    model = None

def get_ats_score(resume_text, job_desc):
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
    if not model: return "Error: API Key Missing"
    prompt = f"""
    Act as a Senior Technical Recruiter. Provide detailed feedback on this candidate.
    Structure your response with:
    1. Strong Matches
    2. Missing Keywords/Skills
    3. Final Verdict (Hire/No Hire)
    
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

# --- NEW FEATURES ---

def generate_cover_letter(resume_text, job_desc):
    if not model: return "Error: API Key Missing"
    prompt = f"""
    Write a professional, persuasive cover letter for this candidate applying to this job.
    Highlight the skills they actually have that match the job.
    Keep it under 300 words.
    
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

def generate_interview_questions(resume_text, job_desc):
    if not model: return "Error: API Key Missing"
    prompt = f"""
    Based on the gaps in this resume compared to the job description, generate 5 targeted interview questions.
    Include 3 technical questions and 2 behavioral questions.
    Provide expected good answers for each.
    
    Resume: {resume_text[:4000]}
    Job: {job_desc[:4000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"
