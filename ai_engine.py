import google.generativeai as genai
import streamlit as st
import os
import time
from google.api_core import exceptions

# --- MODELS TO TRY (Shotgun Approach) ---
# We will try ALL of these until one works.
AVAILABLE_MODELS = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
    'gemini-1.0-pro',
    'gemini-pro'
]

# --- API CONFIGURATION ---
API_KEYS = []
current_key_index = 0

def load_keys():
    """Load keys from secrets into the global list"""
    global API_KEYS
    API_KEYS = [] 
    try:
        # Check numbered keys
        for i in range(1, 11):
            key = st.secrets.get(f"GOOGLE_API_KEY_{i}") or os.environ.get(f"GOOGLE_API_KEY_{i}")
            if key: API_KEYS.append(key.strip())
    except: pass
    
    # Check single key
    single_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if single_key and single_key.strip() not in API_KEYS:
        API_KEYS.append(single_key.strip())

def get_current_key():
    global API_KEYS, current_key_index
    if not API_KEYS: load_keys()
    if not API_KEYS: return None
    return API_KEYS[current_key_index % len(API_KEYS)]

def rotate_key():
    global current_key_index
    if not API_KEYS: load_keys()
    if len(API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        st.toast(f"🔄 Switching to Key #{current_key_index + 1}", icon="🔄")
        return True
    return False

# --- SAFETY SETTINGS ---
# Disable safety filters to ensure report generates
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def generate_smart(prompt):
    """
    Tries multiple keys AND multiple models to get a result.
    """
    max_retries = 2
    last_error_msg = "Unknown Error"
    
    for attempt in range(max_retries):
        key = get_current_key()
        if not key:
            st.error("❌ No API Key found in secrets.toml")
            return None
            
        genai.configure(api_key=key)
        
        # Try each model in our list until one works
        for model_name in AVAILABLE_MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    request_options={"timeout": 30},
                    safety_settings=SAFETY_SETTINGS
                )
                return response
                
            except exceptions.NotFound as e:
                # Capture error but keep trying other models
                last_error_msg = f"Model {model_name} not found (404)"
                continue 
                
            except exceptions.ResourceExhausted as e:
                last_error_msg = f"Quota Exceeded for {model_name}"
                # If quota full, rotate key and retry the whole process
                if rotate_key():
                    time.sleep(1)
                    break 
                else:
                    time.sleep(2)
                    continue
            except Exception as e:
                last_error_msg = f"Error with {model_name}: {str(e)}"
                continue
                
    # If we get here, EVERYTHING failed. Show the LAST error we saw.
    st.error(f"⚠️ AI Failure. Last Reason: {last_error_msg}")
    return None

def get_ats_score(resume_text, job_desc):
    prompt = f"""You are an ATS. Output ONLY a single integer score (0-100).
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}
    Score:"""
    
    response = generate_smart(prompt)
    
    if response:
        try:
            import re
            match = re.search(r'\d+', response.text)
            return int(match.group()) if match else 0
        except: return 0
    return 0

def get_feedback(resume_text, job_desc):
    prompt = f"""Act as a Recruiter. Provide 3 bullet points of feedback.
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}"""
    
    response = generate_smart(prompt)
    
    if response:
        return response.text
    
    return f"⚠️ Could not generate feedback."
