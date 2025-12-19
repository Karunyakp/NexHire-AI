import streamlit as st
import time
import PyPDF2

# --- CRITICAL: THIS MUST BE THE FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="NexHire Platinum", page_icon="💜", layout="wide")

# --- IMPORT LOCAL MODULES AFTER CONFIG ---
import database as db
import ai_engine as ai

# --- SIDEBAR & DIAGNOSTICS ---
with st.sidebar:
    st.write("### Created by Karunya K P")
    
    # --- API KEY CHECKER (Debug Tool) ---
    st.divider()
    st.write("### 🔑 API Key Status")
    if "GOOGLE_API_KEY" in st.secrets:
        st.success("Key Found in Secrets ✅")
    else:
        st.error("Key MISSING ❌")
        st.info("Please add GOOGLE_API_KEY to .streamlit/secrets.toml")
    st.divider()
    
    st.info("Built with Python, Streamlit & Gemini AI")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #111827;
        background-color: #F9FAFB;
    }
    .stApp { background-color: #F9FAFB; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF;
        border-radius: 16px; 
        border: 1px solid #E5E7EB;
        padding: 40px;
    }
    
    div.stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 14px 28px;
        font-weight: 600;
        border: none;
        width: 100%;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Database
db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #4F46E5;'>NexHire</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>Enterprise Recruitment Intelligence</h3>", unsafe_allow_html=True)
            
            tab_sign, tab_reg = st.tabs(["Sign In", "Register"])
            
            with tab_sign:
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.button("Access Dashboard"):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Access Denied.")
            
            with tab_reg:
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        if db.add_user(new_user, new_pass):
                            st.success("Success. Please Log In.")
                        else:
                            st.error("Username taken.")

else:
    # --- DASHBOARD ---
    c_left, c_right = st.columns([6, 1])
    with c_left:
        st.markdown(f"### Hello, {st.session_state['username']}")
            
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.divider()

    history = db.fetch_history(st.session_state['username'])
    last_score = history[0][2] if history else 0
    
    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.markdown("### LATEST SCORE")
            st.markdown(f"<h1 style='margin: 0; color: #4F46E5;'>{last_score}%</h1>", unsafe_allow_html=True)
    with m2:
        with st.container(border=True):
            st.markdown("### TOTAL SCANS")
            st.markdown(f"<h1 style='margin: 0; color: #111827;'>{len(history)}</h1>", unsafe_allow_html=True)
    with m3:
        with st.container(border=True):
            st.markdown("### SYSTEM STATUS")
            st.markdown(f"<h1 style='margin: 0; color: #10B981;'>Online</h1>", unsafe_allow_html=True)

    st.write("")
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        with st.container(border=True):
            st.markdown("### 1. Document Processing")
            uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
            
            resume_text = ""
            if uploaded_file:
                with st.spinner("Reading PDF..."):
                    try:
                        reader = PyPDF2.PdfReader(uploaded_file)
                        for page in reader.pages:
                            resume_text += page.extract_text()
                        st.success("Resume Loaded Successfully")
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
            else:
                resume_text = st.text_area("Or paste resume text here", height=200)

    with col_side:
        with st.container(border=True):
            st.markdown("### 2. Job Requisition")
            job_role = st.text_input("Role Title", placeholder="e.g. Data Scientist")
            job_desc = st.text_area("Job Description", height=250)

    st.write("")
    
    # --- THE ANALYZE BUTTON ---
    if st.button("Initialize Intelligence Engine", type="primary"):
        if resume_text and job_desc:
            with st.spinner("AI is analyzing..."):
                # 1. Get Score
                score = ai.get_ats_score(resume_text, job_desc)
                
                # 2. Get Feedback
                feedback = ai.get_feedback(resume_text, job_desc)
                
                # 3. Save
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.divider()
                
                # 4. Display Results
                r1, r2 = st.columns([1, 2])
                with r1:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown("### COMPATIBILITY")
                        color = "#EF4444" if score < 50 else "#4F46E5"
                        st.markdown(f"<h1 style='font-size: 72px; color: {color}; margin: 0;'>{score}%</h1>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with r2:
                    with st.container(border=True):
                        st.markdown("### AI ASSESSMENT REPORT")
                        st.markdown(feedback)
        else:
            st.warning("Please upload a resume and enter a job description.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: grey;'>© 2025 NexHire Systems</div>", unsafe_allow_html=True)
