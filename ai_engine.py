import google.generativeai as genai
import streamlit as st
import os
import time
from google.api_core import exceptions

# --- MODELS TO TRY (If one fails, we try the next) ---
AVAILABLE_MODELS = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-001',
    'gemini-pro',  # Fallback to 1.0 Pro if Flash fails
]

# --- API CONFIGURATION ---
API_KEYS = []
current_key_index = 0

def load_keys():
    """Load keys from secrets into the global list"""
    global API_KEYS
    API_KEYS = [] 
    
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

def get_current_key():
    global API_KEYS, current_key_index
    if not API_KEYS:
        load_keys()
    if not API_KEYS:
        return None
    return API_KEYS[current_key_index % len(API_KEYS)]

def rotate_key():
    global current_key_index
    if not API_KEYS:
        load_keys()
    if len(API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        st.toast(f"🔄 Switching to Key #{current_key_index + 1}", icon="🔄")
        return True
    return False

# --- SAFETY SETTINGS ---
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

def generate_smart(prompt):
    """
    Universal generation function that handles:
    1. Key Rotation (for 429 Rate Limits)
    2. Model Fallback (for 404 Not Found errors)
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        key = get_current_key()
        if not key:
            st.error("❌ No API Key found.")
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
                
            except exceptions.NotFound:
                # If 404 (Model Not Found), just try the next model in the list
                continue 
                
            except exceptions.ResourceExhausted:
                # If Rate Limit, rotate key and BREAK to outer loop to retry
                if rotate_key():
                    time.sleep(1)
                    break 
                else:
                    time.sleep(2)
                    continue
            except Exception as e:
                # Ignore other errors and keep trying
                pass
                
    st.error("⚠️ AI Service Busy: Could not generate report with any model.")
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
        except:
            return 0
    return 0

def get_feedback(resume_text, job_desc):
    prompt = f"""Act as a Recruiter. Provide 3 bullet points of feedback.
    Resume: {resume_text[:2000]}
    Job: {job_desc[:2000]}"""
    
    response = generate_smart(prompt)
    
    if response:
        return response.text
    
    return "⚠️ Could not generate feedback. Please try again."
    
