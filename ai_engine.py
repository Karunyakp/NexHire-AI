import streamlit as st
import google.generativeai as genai
import json
import random

def configure_genai():
    try:
        # Fetching keys from your specific structure: [general] -> gemini_api_key
        keys = st.secrets["general"]["gemini_api_key"]
        
        # Ensure it's treated as a list even if a single string is returned
        if not isinstance(keys, list): 
            keys = [keys]
            
        random.shuffle(keys)
        for key in keys:
            try:
                genai.configure(api_key=key)
                return True
            except: continue
        return False
    except Exception as e:
        # Silent fail or log for debug if needed
        return False

def get_prompt(name):
    try:
        # Fetching prompts from your specific structure: [prompts] -> name
        return st.secrets["prompts"][name]
    except:
        return ""

def clean_json_text(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text

def generate_json(prompt_name, user_content):
    if not configure_genai(): return None
    
    sys_prompt = get_prompt(prompt_name)
    
    # Fallback if secret is missing (Safety Net)
    if not sys_prompt: 
        if "cand_score_skills" in prompt_name:
            sys_prompt = """You are a Career Coach. Analyze the Resume vs JD. Output JSON ONLY: { "score": int (0-100), "skills": { "matched": [], "partial": [], "missing": [] }, "summary": "2 sentence summary." }"""
        elif "rec_screen" in prompt_name:
             sys_prompt = """You are a Senior Recruiter. Screen this candidate. Output JSON ONLY: { "ats_score": int, "auth_badge": "Human"|"AI", "red_flags": [], "summary": "Text" }"""
        else:
            return None

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nDATA:\n{user_content}"}]}],
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        return json.loads(clean_json_text(resp.text))
    except: return None

def generate_text(prompt_name, user_content):
    if not configure_genai(): return "Service Unavailable (Check API Key)."
    
    sys_prompt = get_prompt(prompt_name)
    if not sys_prompt: sys_prompt = "You are a helpful recruitment AI assistant."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(f"{sys_prompt}\n\nDATA:\n{user_content}")
        return resp.text
    except: return "Generation Error."

def categorize_resume(resume_text):
    # This specific prompt wasn't in your secrets list, so we keep a default or add it if you update secrets
    sys_prompt = "Classify this resume into a SINGLE job category. Output only the name."
    try:
        if configure_genai():
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            resp = model.generate_content(f"{sys_prompt}\n\nRESUME: {resume_text[:2000]}")
            return resp.text.strip()
        return "General"
    except: return "General"

def check_authenticity(resume_text):
    # Mapping to your secret structure if available, or using a default for now since 'authenticity_prompt' wasn't in your snippet
    return generate_json("rec_screen", f"Analyze for AI generation patterns.\nRESUME: {resume_text[:4000]}")

def analyze_fit(resume, jd):
    return generate_json("cand_score_skills", f"RESUME: {resume}\nJD: {jd}")

def get_insights(resume, jd):
    return generate_text("cand_insights", f"RESUME: {resume}\nJD: {jd}")

def get_improvements(resume, jd):
    return generate_text("cand_improve", f"RESUME: {resume}\nJD: {jd}")

def get_interview_prep(resume, jd):
    return generate_text("cand_interview", f"RESUME: {resume}\nJD: {jd}")

def get_roadmap(resume, jd):
    return generate_text("cand_roadmap", f"RESUME: {resume}\nJD: {jd}")

def simulate_skill(resume, jd, current_score, new_skill):
    content = f"Current Score: {current_score}\nNew Skill to Add: {new_skill}\nRESUME: {resume}\nJD: {jd}"
    return generate_json("cand_simulator", content)

def compare_versions(res_v1, res_v2, jd):
    content = f"RESUME V1: {res_v1}\nRESUME V2: {res_v2}\nJD: {jd}"
    return generate_json("cand_compare", content)

def run_screening(resume, jd, bias_free=False):
    bias_note = "Ignore Name, Gender, Location." if bias_free else ""
    # Using python f-string to insert the instruction into your prompt text if needed, 
    # but since your prompt template has {bias_instruction}, we format it here:
    raw_prompt = get_prompt("rec_screen")
    if raw_prompt:
        formatted_prompt = raw_prompt.replace("{bias_instruction}", bias_note)
        # We manually call generate here because we modified the prompt content
        if not configure_genai(): return None
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            resp = model.generate_content(
                contents=[{"role": "user", "parts": [{"text": f"{formatted_prompt}\n\nDATA:\nRESUME: {resume}\nJD: {jd}"}]}],
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(clean_json_text(resp.text))
        except: return None
    
    return generate_json("rec_screen", f"{bias_note}\nRESUME: {resume}\nJD: {jd}")

def explain_score(resume, jd, score):
    content = f"Current Score: {score}\nRESUME: {resume}\nJD: {jd}"
    return generate_text("rec_explain", content)

def chat_response(user_message):
    return generate_text("chatbot_prompt", user_message)

def validate_admin_login(username, password):
    try:
        # Fetching specific admin credentials from [admin] section
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        
        # Strict matching
        if username.strip() == secure_user and password.strip() == secure_pass:
            return True
        return False
    except: return False
