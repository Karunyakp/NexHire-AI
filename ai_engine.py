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
    
    if kwargs:
        try:
            sys_prompt = sys_prompt.format(**kwargs)
        except: pass

    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        resp = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nDATA:\n{content}"}]}],
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        text = resp.text.strip()
        if "
