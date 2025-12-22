import google.generativeai as genai
import streamlit as st
import json
import time
import random

# --- SECURE KEY ROTATION SYSTEM ---
# This prevents "Quota Exceeded" errors by shuffling keys if one fails.
def get_api_key():
    keys = st.secrets["general"]["gemini_api_key"]
    return random.choice(keys)

def get_prompt(prompt_name):
    return st.secrets["prompts"][prompt_name]

def generate_response_with_rotation(contents, retries=3):
    """
    Tries to generate content. If it fails (due to quota), it rotates to a new key.
    """
    attempt = 0
    while attempt < retries:
        try:
            # Pick a random key from the pool
            current_key = get_api_key()
            genai.configure(api_key=current_key)
            
            # Use the faster Flash model for speed
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(contents)
            return response
        except Exception as e:
            # If error is about Quota (429), print warning and retry with new key
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"Key {current_key[:5]}... exhausted. Rotating...")
                attempt += 1
                time.sleep(1) # Brief pause before switching
            else:
                # If it's a real error (not quota), just fail
                print(f"Error: {e}")
                return None
    return None

# --- CORE AI FUNCTIONS ---

def check_resume_authenticity(resume_text):
    """Checks if the resume looks like it was written by AI."""
    sys_prompt = "You are an AI Detector. Analyze if this text is AI-generated. Return JSON: {'is_ai': bool, 'confidence': int, 'reason': str}"
    
    try:
        response = generate_response_with_rotation(f"{sys_prompt}\n\nTEXT: {resume_text[:2000]}")
        # Clean response to ensure pure JSON
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except:
        return {"is_ai": False, "confidence": 0, "reason": "Could not analyze"}

def categorize_resume(resume_text):
    """Determines the job role (e.g. Data Scientist, Web Dev) based on resume content."""
    try:
        response = generate_response_with_rotation(
            f"Classify this resume into ONE job role (e.g. 'Data Scientist', 'Frontend Dev'). Return ONLY the role name.\n\nRESUME: {resume_text[:1000]}"
        )
        return response.text.strip()
    except:
        return "General"

def get_ats_score(resume_text, job_desc):
    """Calculates Match Score and finds missing keywords."""
    sys_prompt = get_prompt("ats_prompt")
    try:
        response = generate_response_with_rotation(
            f"{sys_prompt}\n\nRESUME: {resume_text}\n\nJOB DESCRIPTION: {job_desc}"
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except:
        return {"score": 0, "missing_keywords": [], "summary": "Error analyzing."}

def generate_cover_letter(resume_text, job_desc):
    """Writes a custom cover letter."""
    sys_prompt = get_prompt("cover_letter_prompt")
    try:
        response = generate_response_with_rotation(
            f"{sys_prompt}\n\nRESUME: {resume_text}\n\nJOB DESCRIPTION: {job_desc}"
        )
        return response.text
    except:
        return "Could not generate cover letter."

def generate_interview_questions(resume_text, job_desc):
    """Creates specific interview questions based on gaps."""
    sys_prompt = get_prompt("interview_prompt")
    try:
        response = generate_response_with_rotation(
            f"{sys_prompt}\n\nRESUME: {resume_text}\n\nJOB DESCRIPTION: {job_desc}"
        )
        return response.text
    except:
        return "Could not generate questions."

def get_market_analysis(job_role):
    """Fetches salary and trend data."""
    sys_prompt = get_prompt("market_prompt")
    try:
        response = generate_response_with_rotation(
            f"{sys_prompt}\n\nROLE: {job_role}"
        )
        return response.text
    except:
        return "Could not fetch market data."

def generate_learning_roadmap(missing_keywords, job_role):
    """Creates a study plan for missing skills."""
    sys_prompt = get_prompt("roadmap_prompt")
    try:
        response = generate_response_with_rotation(
            f"{sys_prompt}\n\nROLE: {job_role}\nMISSING SKILLS: {missing_keywords}"
        )
        return response.text
    except:
        return "Could not generate roadmap."

# --- NEW FEATURES FOR STUDENT PREP ---

def refine_bullet_point(bullet_point, job_role):
    """Rewrites a weak bullet point using the STAR method."""
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
    """Grades an interview answer and asks the next question."""
    sys_prompt = get_prompt("interactive_interview_prompt")
    if not sys_prompt: return "Error: Interview Prompt Missing."
    
    try:
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
