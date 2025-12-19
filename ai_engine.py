import google.generativeai as genai
import streamlit as st
import os
import time
from google.api_core import exceptions

# --- API CONFIGURATION WITH KEY ROTATION ---
API_KEYS = []

@st.cache_resource
def initialize_model():
    """Initialize Gemini API with key rotation and better error handling"""
    global API_KEYS
    
    # Try to get all available API keys from secrets
    try:
        for i in range(1, 6):  # Check for up to 5 keys
            key = st.secrets.get(f"GOOGLE_API_KEY_{i}") or os.environ.get(f"GOOGLE_API_KEY_{i}")
            if key:
                API_KEYS.append(key)
    except (FileNotFoundError, AttributeError):
        pass
    
    # Also check for single key
    single_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if single_key and single_key not in API_KEYS:
        API_KEYS.append(single_key)
    
    if not API_KEYS:
        st.error("❌ No GOOGLE_API_KEY found. Please configure API keys in .streamlit/secrets.toml")
        return None
    
    # Try to initialize with first key
    try:
        genai.configure(api_key=API_KEYS[0])
        model = genai.GenerativeModel('gemini-1.5-flash')  # Using flash for faster responses
        return model
    except Exception as e:
        st.error(f"❌ API Initialization Error: {str(e)}")
        return None

# Initialize model once
model = initialize_model()
current_key_index = 0

def rotate_api_key():
    """Rotate to next available API key"""
    global current_key_index, model
    if len(API_KEYS) > 1:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        try:
            genai.configure(api_key=API_KEYS[current_key_index])
            model = genai.GenerativeModel('gemini-1.5-flash')
            st.info(f"🔄 Switched to API Key {current_key_index + 1}/{len(API_KEYS)}")
            return True
        except Exception as e:
            st.error(f"❌ Failed to rotate key: {str(e)}")
            return False
    return False

def get_ats_score(resume_text, job_desc):
    """Get ATS compatibility score with retry logic and key rotation"""
    global model
    if not model:
        st.error("❌ AI Engine not initialized")
        return 0
    
    prompt = f"""You are an ATS (Applicant Tracking System). 
Compare the resume with the job description and provide ONLY a single integer score from 0 to 100.
Do not provide any other text, just the number.

Resume (first 2000 chars):
{resume_text[:2000]}

Job Description (first 2000 chars):
{job_desc[:2000]}

Score:"""
    
    try:
        response = model.generate_content(prompt, request_options={"timeout": 30})
        score_text = ''.join(filter(str.isdigit, response.text))
        score = int(score_text) if score_text else 0
        return min(100, max(0, score))  # Ensure score is between 0-100
    
    except exceptions.ResourceExhausted as e:
        st.warning("⏱️ Rate limit reached. Attempting to use alternative API key...")
        if rotate_api_key():
            time.sleep(2)
            # Retry with new key
            try:
                response = model.generate_content(prompt, request_options={"timeout": 30})
                score_text = ''.join(filter(str.isdigit, response.text))
                return int(score_text) if score_text else 50
            except:
                return 50
        return 50
    
    except exceptions.DeadlineExceeded:
        st.error("⏱️ Request timed out. Please try again.")
        return 0
    
    except Exception as e:
        st.error(f"❌ Error calculating score: {str(e)[:100]}")
        return 0

def get_feedback(resume_text, job_desc):
    """Get AI feedback with error handling and key rotation"""
    global model
    if not model:
        return "❌ Error: AI Engine not initialized"
    
    prompt = f"""You are an experienced recruiter and hiring manager.
Analyze the candidate's resume against the job requirements and provide feedback.
Format your response as 3 bullet points. Be concise and actionable.

Resume:
{resume_text[:1500]}

Job Description:
{job_desc[:1500]}

Provide 3 specific feedback points:"""
    
    try:
        response = model.generate_content(prompt, request_options={"timeout": 30})
        return response.text
    
    except exceptions.ResourceExhausted as e:
        st.warning("⏱️ Rate limit reached. Attempting to use alternative API key...")
        if rotate_api_key():
            time.sleep(2)
            try:
                response = model.generate_content(prompt, request_options={"timeout": 30})
                return response.text
            except:
                return "Unable to generate detailed feedback. Please try again in a moment."
        return "Rate limit reached. Please try again in a few moments."
    
    except exceptions.DeadlineExceeded:
        st.error("⏱️ Request timed out. Please try again.")
        return "Request timed out. Please try again."
    
    except Exception as e:
        return f"⚠️ Error generating feedback: {str(e)[:100]}"
