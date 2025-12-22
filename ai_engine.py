import streamlit as st
import google.generativeai as genai
import json
import random
import time

# --- HELPER: SMART KEY ROTATION ---
def generate_response_with_rotation(contents, generation_config=None):
    """
    Tries to generate content using the list of API keys.
    If one key hits a quota limit (429), it rotates to the next one.
    """
    try:
        keys = st.secrets["general"]["gemini_api_key"]
        # Ensure keys is a list
        if not isinstance(keys, list):
            keys = [keys]
            
        # Shuffle keys to distribute load across different scans
        random.shuffle(keys)
    except:
        # Fallback if secrets are missing
        st.error("🚨 API Keys missing in Secrets!")
        return None

    last_error = None
    
    for api_key in keys:
        try:
            # Configure with the current key
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            # Attempt generation
            response = model.generate_content(
                contents=contents, 
                generation_config=generation_config
            )
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            # If it's a Quota/Limit error, log it and TRY NEXT KEY
            if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                last_error = e
                continue 
            else:
                # If it's a logic error (like bad prompt), fail immediately
                raise e
    
    # If we loop through ALL keys and they all fail
    raise last_error if last_error else Exception("All API keys are exhausted or invalid.")

def get_prompt(prompt_name):
    try:
        return st.secrets["prompts"][prompt_name]
    except:
        return None

# --- CORE AI FUNCTIONS ---

def check_resume_authenticity(resume_text):
    sys_prompt = get_prompt("authenticity_prompt")
    if not sys_prompt: return {"human_score": 0, "verdict": "Error", "analysis": "Prompt Missing from Secrets."}

    try:
        # Use Rotation Helper
        response = generate_response_with_rotation(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nRESUME TEXT:\n{resume_text[:4000]}"}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response: return {"human_score": 0, "verdict": "Error", "analysis": "API Error"}

        text_out = response.text.strip()
        if "```json" in text_out:
            text_out = text_out.split("```json")[1].split("```")[0]
        elif "```" in text_out:
            text_out = text_out.split("```")[1].split("```")[0]
            
        return json.loads(text_out)
    except Exception as e:
        return {"human_score": 0, "verdict": "Error", "analysis": f"Analysis Failed: {str(e)}"}

def categorize_resume(resume_text):
    sys_prompt = get_prompt("category_prompt")
    if not sys_prompt: return "General Profile"
    
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nResume Snippet:\n{resume_text[:2000]}"
        )
        return response.text.strip() if response else "General Professional"
    except:
        return "General Professional"

def get_ats_score(resume_text, job_desc):
    sys_prompt = get_prompt("ats_prompt")
    if not sys_prompt: return 0, []

    try:
        full_prompt = f"{sys_prompt}\n\nRESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
        
        response = generate_response_with_rotation(
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response: return 0, []

        text_out = response.text.strip()
        if "```json" in text_out:
            text_out = text_out.split("```json")[1].split("```")[0]
        elif "```" in text_out:
            text_out = text_out.split("```")[1].split("```")[0]
            
        data = json.loads(text_out)
        return int(data.get("score", 0)), data.get("missing_keywords", [])
    except Exception as e:
        return 0, []

def get_feedback(resume_text, job_desc):
    sys_prompt = get_prompt("ats_prompt") 
    if not sys_prompt: return "Error: System Prompts Missing."

    try:
        full_prompt = f"{sys_prompt}\n\nRESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_desc}"
        
        response = generate_response_with_rotation(
            contents=[{"role": "user", "parts": [{"text": full_prompt}]}],
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response: return "Analysis Failed."

        text_out = response.text.strip()
        if "```json" in text_out:
            text_out = text_out.split("```json")[1].split("```")[0]
        elif "```" in text_out:
            text_out = text_out.split("```")[1].split("```")[0]
            
        data = json.loads(text_out)
        return data.get("summary", "Analysis failed.")
    except:
        return "Could not generate feedback."

def generate_cover_letter(resume_text, job_desc):
    sys_prompt = get_prompt("cover_letter_prompt")
    if not sys_prompt: return "Cover Letter Module Locked."
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nCandidate Resume: {resume_text}\n\nTarget Job: {job_desc}"
        )
        return response.text if response else "Error generating draft."
    except:
        return "Could not generate draft."

def generate_interview_questions(resume_text, job_desc):
    sys_prompt = get_prompt("interview_prompt")
    if not sys_prompt: return "Interview Module Locked."
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nResume: {resume_text}\n\nJob: {job_desc}"
        )
        return response.text if response else "Error generating questions."
    except:
        return "Could not generate questions."

def get_market_analysis(resume_text, role):
    sys_prompt = get_prompt("market_prompt")
    if not sys_prompt: return "Market Analysis Module Locked."
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nJob Role: {role}\nResume Context: {resume_text[:2000]}"
        )
        return response.text if response else "Market analysis unavailable."
    except:
        return "Market analysis unavailable."

def generate_learning_roadmap(resume_text, job_desc):
    sys_prompt = get_prompt("roadmap_prompt")
    if not sys_prompt: return "Roadmap Module Locked."
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nResume: {resume_text}\nJob Description: {job_desc}"
        )
        return response.text if response else "Roadmap unavailable."
    except:
        return "Roadmap unavailable."

def generate_email_draft(resume_text, role, email_type):
    sys_prompt = get_prompt("email_prompt")
    if not sys_prompt: return "Email Module Locked."
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nEmail Type: {email_type}\nRole: {role}\nResume Context: {resume_text[:1000]}"
        )
        return response.text if response else "Email draft unavailable."
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
# --- ADD THIS TO THE BOTTOM OF ai_engine.py ---

def refine_bullet_point(bullet_point, job_role):
    sys_prompt = get_prompt("polisher_prompt")
    if not sys_prompt: return "Error: Polisher Prompt Missing."
    
    try:
        response = generate_response_with_rotation(
            contents=f"{sys_prompt}\n\nTarget Role: {job_role}\nOriginal Text: {bullet_point}"
        )
        return response.text if response else "Could not refine text."
    except:
        return "Error refining text."

def evaluate_interview_answer(current_question, user_answer, resume_context):
    sys_prompt = get_prompt("interactive_interview_prompt")
    if not sys_prompt: return "Error: Interview Prompt Missing."
    
    try:
        # We send the whole context so the AI knows what's happening
        prompt_content = f"""
        {sys_prompt}
        
        RESUME CONTEXT: {resume_context[:1000]}
        
        CURRENT QUESTION: {current_question}
        CANDIDATE ANSWER: {user_answer}
        """
        
        response = generate_response_with_rotation(
            contents=prompt_content
        )
        return response.text if response else "Could not evaluate answer."
    except:
        return "Error evaluating answer."
