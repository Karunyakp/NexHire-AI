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
    return st.secrets["prompts"].get(name, "")

def generate_json(prompt_name, content, **kwargs):
    if not configure_genai(): return None
    sys_prompt = get_prompt(prompt_name)
    if not sys_prompt: return None
    
    # Only format if kwargs exist (prevents breaking JSON braces in simple prompts)
    if kwargs:
        try:
            sys_prompt = sys_prompt.format(**kwargs)
        except Exception as e:
            print(f"Prompt formatting error: {e}")
            # Fallback: Use raw prompt if formatting fails
            pass

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nDATA:\n{content}"}]}],
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        text = resp.text.strip()
        # Clean markdown if present
        if "```json" in text: 
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text: 
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except: return None

def generate_text(prompt_name, content, **kwargs):
    if not configure_genai(): return "Error: AI Unavailable"
    sys_prompt = get_prompt(prompt_name)
    
    if kwargs:
        try:
            sys_prompt = sys_prompt.format(**kwargs)
        except: pass

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(f"{sys_prompt}\n\nDATA:\n{content}")
        return resp.text
    except: return "Error generating text."

# --- 🎓 CANDIDATE FUNCTIONS ---
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
    return generate_json("cand_simulator", f"RESUME: {resume}\nJD: {jd}", current_score=current_score, new_skill=new_skill)

def compare_versions(res_v1, res_v2, jd):
    return generate_json("cand_compare", f"RESUME V1: {res_v1}\nRESUME V2: {res_v2}\nJD: {jd}")

# --- 🧑‍💼 RECRUITER FUNCTIONS ---
def run_screening(resume, jd, bias_free=False):
    # Dynamic prompt injection for Bias-Free mode
    bias_instr = "IMPORTANT: IGNORE the candidate's Name, Gender, University Name, and Location. Focus ONLY on Skills and Experience." if bias_free else ""
    return generate_json("rec_screen", f"RESUME: {resume}\nJD: {jd}", bias_instruction=bias_instr)

def explain_score(resume, jd, score):
    return generate_text("rec_explain", f"Current Score: {score}\nRESUME: {resume}\nJD: {jd}")

# --- 🔐 SECURITY FUNCTIONS ---
def validate_admin_login(username, password):
    try:
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        if username == secure_user and password == secure_pass:
            return True
        return False
    except:
        return False
