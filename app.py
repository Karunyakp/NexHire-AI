import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire Enterprise", page_icon="💼", layout="wide")

# --- CLEAN & READABLE CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    /* 1. CLEAN BACKGROUND (No Images, just soft gradient) */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* 2. HIDE JUNK */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3. SOLID WHITE LOGIN CARD (100% Readable) */
    .login-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); /* Soft shadow for depth */
        margin-top: 50px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }

    /* 4. INPUT FIELDS */
    .stTextInput>div>div>input {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 12px;
        border-radius: 8px;
        color: #0f172a; /* Dark text */
    }
    .stTextInput>div>div>input:focus {
        border-color: #2563eb;
        background-color: #ffffff;
    }

    /* 5. BUTTONS */
    .stButton>button {
        background-color: #2563eb; /* Corporate Blue */
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }

    /* 6. TEXT STYLES */
    h1 { color: #0f172a; font-weight: 800; font-size: 2.5rem; margin-bottom: 0;}
    p { color: #64748b; font-size: 1rem; margin-top: 5px; }
    
    /* 7. TABS */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# ==========================================
# 🔒 CLEAN LOGIN SCREEN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Start Card
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Title
        st.markdown("<h1>NexHire</h1>", unsafe_allow_html=True)
        st.markdown("<p>Enterprise AI Assessment Portal</p>", unsafe_allow_html=True)
        st.write("") # Space
        
        tab1, tab2 = st.tabs(["Sign In", "New Account"])
        
        with tab1:
            st.write("")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            st.write("")
            if st.button("Log In"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Incorrect credentials.")
        
        with tab2:
            st.write("")
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            st.write("")
            if st.button("Create Account"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.success("Account created!")
                    else:
                        st.error("Username taken.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📊 CLEAN DASHBOARD
# ==========================================
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['username']}")
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()
        
        st.markdown("### History")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.info(f"{item[1]}: {item[2]}%")

    # Main Area
    st.title("Resume Analysis Dashboard")
    st.markdown("Upload a resume to begin AI assessment.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Upload Resume")
        uploaded_file = st.file_uploader("PDF Document", type="pdf")
        resume_text = ""
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("File uploaded.")
        else:
            resume_text = st.text_area("Or paste text", height=200)

    with col2:
        st.markdown("### 2. Job Description")
        job_role = st.text_input("Role Title")
        job_desc = st.text_area("Paste JD", height=200)

    st.markdown("---")
    if st.button("Run Analysis"):
        if resume_text and job_desc:
            with st.spinner("Analyzing..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                col_res1, col_res2 = st.columns([1, 2])
                with col_res1:
                    st.metric("Match Score", f"{score}%")
                with col_res2:
                    st.info(feedback)
        else:
            st.warning("Please fill all fields.")