import streamlit as st
import google.generativeai as genai
import json
import random

# --- CONFIGURATION ---
def configure_genai():
    try:
        # Fetch API Key from Streamlit Secrets
        # Supports both single string OR list of keys (Rotation)
        keys = st.secrets["general"]["gemini_api_key"]
        
        if isinstance(keys, list):
            api_key = random.choice(keys) # Pick a random key from the list
        else:
            api_key = keys # Use the single key provided
            
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"🚨 SECURITY CHECK FAILED: API Key missing or invalid. Error: {str(e)}")
        return False

# --- HELPER: GET PROMPTS ---
def get_prompt(prompt_name):
    try:
        return st.secrets["prompts"][prompt_name]
    except:
        return None

# --- ADMIN SECURITY (NEW) ---
def validate_admin_login(username, password):
    """
    Verifies admin credentials against the secure cloud vault (secrets.toml).
    This hides the admin username/password from the public code.
    """
    try:
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        
        # Check for exact match
        if username == secure_user and password == secure_pass:
            return True
        return False
    except Exception as e:
        # If secrets are missing or incorrect, admin login fails securely
        return False

# --- CORE AI FUNCTIONS ---

def get_ats_score(resume_text, job_desc):
    if not configure_genai(): return 0
    
    sys_prompt = get_prompt("ats_prompt")
    if not sys_prompt: return 0 

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        full_prompt = f"{sys_prompt}\n\nRESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
        
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        
        data = json.loads(response.text)
        return int(data.get("score", 0))
    except Exception as e:
        return 0

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

# --- STRATEGIC INSIGHTS ---

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
