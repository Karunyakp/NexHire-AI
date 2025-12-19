import google.generativeai as genai
import streamlit as st
import os
import time
from google.api_core import exceptions

# --- API CONFIGURATION WITH KEY ROTATION ---
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
    
    # If we already have a working model, return it
    if model:
        return model

    # Otherwise, load keys and start fresh
    load_keys()
    
    if not API_KEYS:
        st.error("❌ No GOOGLE_API_KEY found in secrets.")
        return None
        
    try:
        # Configure with the current key
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
            st.info(f"🔄 Switched to Key #{current_key_index + 1}")
            return True
        except Exception as e:
            return False
    return False

def get_ats_score(resume_text, job_desc):
    """Get ATS score with lazy loading"""
    # Initialize model NOW, not at startup
    active_model = get_model()
    
    if not active_model:
        return 0
    
    prompt = f"""You are an ATS. Output ONLY a single integer score (0-100).
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}
    Score:"""
    
    try:
        response = active_model.generate_content(prompt, request_options={"timeout": 30})
        import re
        match = re.search(r'\d+', response.text)
        return int(match.group()) if match else 0
    
    except exceptions.ResourceExhausted:
        if rotate_api_key():
            time.sleep(1)
            return get_ats_score(resume_text, job_desc) # Retry
        return 0
    except Exception:
        return 0

def get_feedback(resume_text, job_desc):
    """Get Feedback with lazy loading"""
    # Initialize model NOW, not at startup
    active_model = get_model()
    
    if not active_model:
        return "AI Error"
    
    prompt = f"""Act as a Recruiter. Provide 3 bullet points of feedback.
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}"""
    
    try:
        response = active_model.generate_content(prompt, request_options={"timeout": 30})
        return response.text
    
    except exceptions.ResourceExhausted:
        if rotate_api_key():
            time.sleep(1)
            return get_feedback(resume_text, job_desc)
        return "Rate limit reached."
    except Exception as e:
        return "Error generating feedback."
