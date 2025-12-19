import google.generativeai as genai
import streamlit as st
import os
import time
from google.api_core import exceptions

# --- API CONFIGURATION ---
API_KEYS = []
model = None
current_key_index = 0

def load_keys():
    """Load keys from secrets into the global list"""
    global API_KEYS
    API_KEYS = [] # Reset
    
    # Check numbered keys
    try:
        for i in range(1, 11):
            key = st.secrets.get(f"GOOGLE_API_KEY_{i}") or os.environ.get(f"GOOGLE_API_KEY_{i}")
            if key:
                API_KEYS.append(key)
    except:
        pass
    
    # Check single key
    single_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if single_key and single_key not in API_KEYS:
        API_KEYS.append(single_key)

def get_model():
    """Get or initialize the model. Only runs when needed."""
    global model, current_key_index
    
    if model:
        return model

    load_keys()
    
    if not API_KEYS:
        st.error("❌ No GOOGLE_API_KEY found in secrets.")
        return None
        
    try:
        genai.configure(api_key=API_KEYS[current_key_index])
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        st.error(f"Error initializing AI: {e}")
        return None

def rotate_api_key():
    """Rotate to next available API key"""
    global current_key_index, model
    
    if not API_KEYS:
        load_keys()
        
    if len(API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        try:
            genai.configure(api_key=API_KEYS[current_key_index])
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.toast(f"🔄 Switched to Key #{current_key_index + 1}", icon="🔄")
            return True
        except Exception:
            return False
    return False

# --- SAFETY SETTINGS (CRITICAL FOR RESUMES) ---
# Resumes often trigger false "Harassment" or "Personal Info" blocks.
# We disable these blocks so the report always generates.
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def get_ats_score(resume_text, job_desc):
    active_model = get_model()
    if not active_model: return 0
    
    prompt = f"""You are an ATS. Output ONLY a single integer score (0-100).
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}
    Score:"""
    
    try:
        response = active_model.generate_content(
            prompt, 
            request_options={"timeout": 30},
            safety_settings=SAFETY_SETTINGS
        )
        import re
        match = re.search(r'\d+', response.text)
        return int(match.group()) if match else 0
    
    except exceptions.ResourceExhausted:
        if rotate_api_key():
            time.sleep(1)
            return get_ats_score(resume_text, job_desc)
        return 0
    except Exception:
        return 0

def get_feedback(resume_text, job_desc):
    active_model = get_model()
    if not active_model: return "❌ Error: AI Model not loaded."
    
    prompt = f"""Act as a Recruiter. Provide 3 bullet points of feedback.
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}"""
    
    try:
        response = active_model.generate_content(
            prompt, 
            request_options={"timeout": 30},
            safety_settings=SAFETY_SETTINGS
        )
        return response.text
    
    except exceptions.ResourceExhausted:
        if rotate_api_key():
            time.sleep(1)
            return get_feedback(resume_text, job_desc)
        return "⚠️ Rate limit reached. Please try again in 30 seconds."
        
    except Exception as e:
        # This will now print the REAL error to your app screen
        return f"⚠️ Report Generation Error: {str(e)}"
