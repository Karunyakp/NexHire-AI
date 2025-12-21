import streamlit as st
import google.generativeai as genai
import json
import random

# --- CONFIGURATION ---
def configure_genai():
    try:
        keys = st.secrets["general"]["gemini_api_key"]
        if not isinstance(keys, list): keys = [keys]
        random.shuffle(keys)
        for key in keys:
            try:
                genai.configure(api_key=key)
                return True
            except: continue
        return False
    except: return False

def get_prompt(name):
    # Safe fetch
    try:
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
    if not sys_prompt: return None

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nDATA:\n{user_content}"}]}],
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        return json.loads(clean_json_text(resp.text))
    except: return None

def generate_text(prompt_name, user_content):
    if not configure_genai(): return "Error: AI Unavailable"
    sys_prompt = get_prompt(prompt_name)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(f"{sys_prompt}\n\nDATA:\n{user_content}")
        return resp.text
    except: return "Error generating text."

# --- 🎓 CANDIDATE FUNCTIONS ---

def categorize_resume(resume_text):
    # Simple categorization (RESTORED FEATURE)
    sys_prompt = "Classify this resume into a SINGLE job category (e.g. Full Stack Dev). Output only the name."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(f"{sys_prompt}\n\nRESUME: {resume_text[:2000]}")
        return resp.text.strip()
    except: return "General"

def check_authenticity(resume_text):
    # Authenticity Check (RESTORED FEATURE)
    return generate_json("authenticity_prompt", f"RESUME: {resume_text[:4000]}")

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
    # Pass variables in user content instead of formatting system prompt
    content = f"Current Score: {current_score}\nNew Skill to Add: {new_skill}\nRESUME: {resume}\nJD: {jd}"
    return generate_json("cand_simulator", content)

def compare_versions(res_v1, res_v2, jd):
    content = f"RESUME V1: {res_v1}\nRESUME V2: {res_v2}\nJD: {jd}"
    return generate_json("cand_compare", content)

# --- 🧑‍💼 RECRUITER FUNCTIONS ---
def run_screening(resume, jd, bias_free=False):
    bias_note = "NOTE: Ignore Name, Gender, Location." if bias_free else ""
    content = f"{bias_note}\nRESUME: {resume}\nJD: {jd}"
    return generate_json("rec_screen", content)

def explain_score(resume, jd, score):
    content = f"Current Score: {score}\nRESUME: {resume}\nJD: {jd}"
    return generate_text("rec_explain", content)

# --- 🔐 SECURITY ---
def validate_admin_login(username, password):
    try:
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        if username == secure_user and password == secure_pass:
            return True
        return False
    except: return False
