import streamlit as st
import google.generativeai as genai
import json
import random

# --- CONFIGURATION ---
def configure_genai():
    try:
        keys = st.secrets["general"]["gemini_api_key"]
        if isinstance(keys, list):
            api_key = random.choice(keys)
        else:
            api_key = keys
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"🚨 SECURITY CHECK FAILED: API Key missing. Error: {str(e)}")
        return False

def get_prompt(prompt_name):
    try:
        return st.secrets["prompts"][prompt_name]
    except:
        return None

# --- CORE AI FUNCTIONS ---

def check_resume_authenticity(resume_text):
    """
    Analyzes the resume to see if it looks AI-generated or Human-written.
    Also checks basic ATS readability.
    """
    if not configure_genai(): return {"human_score": 0, "verdict": "Error", "analysis": "Security Error"}
    
    sys_prompt = get_prompt("authenticity_prompt")
    if not sys_prompt: return {"human_score": 0, "verdict": "Error", "analysis": "Prompt Missing"}

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nRESUME TEXT:\n{resume_text[:4000]}"}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except:
        return {"human_score": 0, "verdict": "Error", "analysis": "Could not analyze text."}

def categorize_resume(resume_text):
    if not configure_genai(): return "Uncategorized"
    sys_prompt = get_prompt("category_prompt")
    if not sys_prompt: return "General Profile"
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nResume Snippet:\n{resume_text[:2000]}")
        return response.text.strip()
    except:
        return "General Professional"

def get_ats_score(resume_text, job_desc):
    if not configure_genai(): return 0, []
    sys_prompt = get_prompt("ats_prompt")
    if not sys_prompt: return 0, []

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        full_prompt = f"{sys_prompt}\n\nRESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
        
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        
        data = json.loads(response.text)
        return int(data.get("score", 0)), data.get("missing_keywords", [])
    except Exception as e:
        return 0, []

def get_feedback(resume_text, job_desc):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("ats_prompt") 
    if not sys_prompt: return "Error: System Prompts Missing."

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        full_prompt = f"{sys_prompt}\n\nRESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
        
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        return data.get("summary", "Analysis failed.")
    except:
        return "Could not generate feedback."

def generate_cover_letter(resume_text, job_desc):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("cover_letter_prompt")
    if not sys_prompt: return "Cover Letter Module Locked."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nCandidate Resume: {resume_text}\n\nTarget Job: {job_desc}")
        return response.text
    except:
        return "Could not generate draft."

def generate_interview_questions(resume_text, job_desc):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("interview_prompt")
    if not sys_prompt: return "Interview Module Locked."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nResume: {resume_text}\n\nJob: {job_desc}")
        return response.text
    except:
        return "Could not generate questions."

def get_market_analysis(resume_text, role):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("market_prompt")
    if not sys_prompt: return "Market Analysis Module Locked."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nJob Role: {role}\nResume Context: {resume_text[:2000]}")
        return response.text
    except:
        return "Market analysis unavailable."

def generate_learning_roadmap(resume_text, job_desc):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("roadmap_prompt")
    if not sys_prompt: return "Roadmap Module Locked."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nResume: {resume_text}\nJob Description: {job_desc}")
        return response.text
    except:
        return "Roadmap unavailable."

def generate_email_draft(resume_text, role, email_type):
    if not configure_genai(): return "Security Error."
    sys_prompt = get_prompt("email_prompt")
    if not sys_prompt: return "Email Module Locked."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(f"{sys_prompt}\n\nEmail Type: {email_type}\nRole: {role}\nResume Context: {resume_text[:1000]}")
        return response.text
    except:
        return "Email draft unavailable."
    
def validate_admin_login(username, password):
    try:
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        if username == secure_user and password == secure_pass:
            return True
        return False
    except:
        return False
