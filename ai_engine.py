import streamlit as st
import google.generativeai as genai
import json
import random
import time

def get_keys():
  
    try:
        keys = st.secrets["general"]["gemini_api_key"]
        if not isinstance(keys, list):
            return [keys]
        # Shuffle to distribute load
        random.shuffle(keys)
        return keys
    except:
        return []

def get_prompt(name):
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

def generate_with_retry(system_prompt, user_content, response_mime_type="text/plain"):
    """
    Tries to generate content using available keys. 
    If a key fails (quota exceeded), it tries the next one.
    """
    keys = get_keys()
    if not keys:
        return None

    for key in keys:
        try:
            # Configure with the current key attempt
            genai.configure(api_key=key)
            
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
            
            generation_config = {"temperature": 0.0}
            if response_mime_type == "application/json":
                generation_config["response_mime_type"] = "application/json"

            # Attempt generation
            resp = model.generate_content(
                contents=[{"role": "user", "parts": [{"text": f"{system_prompt}\n\nDATA:\n{user_content}"}]}],
                generation_config=generation_config
            )
         
            return resp.text
            
        except Exception as e:
            # If error is quota related (429) or other API issue, log/continue to next key
            # print(f"Key failed: {e}") # Debugging
            continue
            

    return None

def generate_json(prompt_name, user_content):
    sys_prompt = get_prompt(prompt_name)
    if not sys_prompt: 
      
        if "cand_score_skills" in prompt_name:
            sys_prompt = "Analyze the resume. Output JSON: { 'score': 0, 'skills': {'matched':[], 'partial':[], 'missing':[]}, 'summary': '' }"
        elif "rec_screen" in prompt_name:
            sys_prompt = "Screen candidate. Output JSON: { 'ats_score': 0, 'auth_badge': 'Unknown', 'red_flags': [], 'summary': '' }"
        else:
            return None

    result_text = generate_with_retry(sys_prompt, user_content, response_mime_type="application/json")
    
    if result_text:
        try:
            return json.loads(clean_json_text(result_text))
        except:
            return None
    return None

def generate_text(prompt_name, user_content):
    sys_prompt = get_prompt(prompt_name)
    if not sys_prompt: sys_prompt = "You are a helpful recruitment AI assistant."
    
    result_text = generate_with_retry(sys_prompt, user_content, response_mime_type="text/plain")
    
    if result_text:
        return result_text
    return "Service Unavailable (All API keys exhausted or invalid)."


def categorize_resume(resume_text):
    sys_prompt = "Classify this resume into a SINGLE job category. Output only the name."
    res = generate_with_retry(sys_prompt, f"RESUME: {resume_text[:2000]}")
    return res.strip() if res else "General"

def check_authenticity(resume_text):
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
    content = f"Current Score: {current_score}\nNew Skill to Add: {new_skill}\nRESUME: {resume}\nJD: {jd}"
    return generate_json("cand_simulator", content)

def compare_versions(res_v1, res_v2, jd):
    content = f"RESUME V1: {res_v1}\nRESUME V2: {res_v2}\nJD: {jd}"
    return generate_json("cand_compare", content)

def run_screening(resume, jd, bias_free=False):
    bias_note = "Ignore Name, Gender, Location." if bias_free else ""

    content = f"{bias_note}\nRESUME: {resume}\nJD: {jd}"
    
 
    raw_prompt = get_prompt("rec_screen")
    if raw_prompt and "{bias_instruction}" in raw_prompt:
        formatted_sys_prompt = raw_prompt.replace("{bias_instruction}", bias_note)
        # Call low-level generation directly with formatted prompt
        res_text = generate_with_retry(formatted_sys_prompt, f"RESUME: {resume}\nJD: {jd}", "application/json")
        if res_text:
            return json.loads(clean_json_text(res_text))
        return None
        
    return generate_json("rec_screen", content)

def explain_score(resume, jd, score):
    content = f"Current Score: {score}\nRESUME: {resume}\nJD: {jd}"
    return generate_text("rec_explain", content)

def chat_response(user_message):
    return generate_text("chatbot_prompt", user_message)

def validate_admin_login(username, password):
    try:
        secure_user = st.secrets["admin"]["username"]
        secure_pass = st.secrets["admin"]["password"]
        if username == secure_user and password == secure_pass:
            return True
        return False
    except: return False

