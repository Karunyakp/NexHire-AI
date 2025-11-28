import google.generativeai as genai
import streamlit as st

# --- API CONFIGURATION ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    API_KEY = "PASTE_YOUR_KEY_HERE"

if API_KEY != "PASTE_YOUR_KEY_HERE":
    genai.configure(api_key=API_KEY)
    # 🔴 WE ARE USING THE NEWEST FLASH MODEL
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

def get_ats_score(resume_text, job_desc):
    if not model: return 0
    
    prompt = f"""
    You are an ATS. Compare the Resume to the Job Description.
    Output ONLY a single integer from 0 to 100.
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
    Act as a Recruiter. Provide 3 feedback points.
    Resume: {resume_text[:3000]}
    Job: {job_desc[:3000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"