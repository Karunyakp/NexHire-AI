import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire Enterprise", page_icon="🛡️", layout="wide")

# --- ENTERPRISE CSS DESIGN SYSTEM ---
st.markdown("""
    <style>
    /* 1. IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* 2. GLOBAL RESET */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* 3. BACKGROUND */
    .stApp {
        background-color: #F5F7FA;
    }
    
    /* 4. HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 5. THE LOGIN CARD CONTAINER */
    .login-card {
        background-color: #ffffff;
        padding: 40px 32px;
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* 6. TYPOGRAPHY */
    .brand-logo {
        font-size: 40px;
        color: #1F3C88;
        margin-bottom: 10px;
    }
    .brand-title {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 15px;
        color: #6B7280;
        font-weight: 400;
        margin-top: 8px;
        margin-bottom: 24px;
    }
    
    /* 7. INPUT FIELDS (OVERRIDING STREAMLIT DEFAULTS) */
    .stTextInput > div > div > input {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        color: #1F2937;
        background-color: #FFFFFF;
        transition: border 0.2s, box-shadow 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1F3C88;
        box-shadow: 0 0 0 3px rgba(31, 60, 136, 0.1);
    }
    
    /* 8. BUTTONS (PRIMARY ACTION) */
    .stButton > button {
        width: 100%;
        background-color: #1F3C88;
        color: #ffffff;
        font-weight: 600;
        padding: 12px 0;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        transition: background-color 0.2s;
        height: 48px;
    }
    .stButton > button:hover {
        background-color: #162a60; /* Darker Navy on Hover */
        color: #ffffff;
    }
    
    /* 9. TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        color: #6B7280;
        font-weight: 500;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #1F3C88; /* Active Tab Color */
        border-bottom: 2px solid #1F3C88;
        font-weight: 600;
    }
    
    /* DASHBOARD CARD STYLES */
    .dashboard-card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Database
db.create_tables()

# Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# ==========================================
# 🔐 LOGIN SCREEN (ENTERPRISE DESIGN)
# ==========================================
if not st.session_state['logged_in']:
    
    # We use columns to force the card to the center.
    # Ratios: [1, 1.2, 1] makes the middle column narrow and centered.
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        # --- HEADER SECTION ---
        # We inject a specific DIV structure to match your requested design
        st.markdown("""
        <div class="login-card">
            <div class="brand-logo">🛡️</div>
            <h1 class="brand-title">NexHire Enterprise</h1>
            <p class="brand-subtitle">Secure AI Assessment Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        # --- TABS SECTION ---
        # We put the inputs OUTSIDE the HTML div so Streamlit logic still works,
        # but we style them using the CSS above.
        tab1, tab2 = st.tabs(["SIGN IN", "REGISTER"])
        
        with tab1:
            username = st.text_input("Username / Email", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            st.write("") # Spacer
            
            if st.button("Sign In"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Authentication failed. Please check credentials.")
            
            # Secondary Actions
            st.markdown("""
            <div style="text-align: center; margin-top: 16px;">
                <a href="#" style="color: #6B7280; text-decoration: none; font-size: 13px;">Forgot password?</a>
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            new_user = st.text_input("New Username", key="new_user", placeholder="Choose a username")
            new_pass = st.text_input("New Password", type="password", key="new_pass", placeholder="Choose a strong password")
            st.write("") # Spacer
            
            if st.button("Create Account"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.success("Account created successfully.")
                    else:
                        st.error("Username is not available.")
                else:
                    st.warning("All fields are required.")

# ==========================================
# 🚀 DASHBOARD (ENTERPRISE STYLE)
# ==========================================
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['username']}")
        st.caption("Enterprise Account")
        st.markdown("---")
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.markdown("### Audit Logs")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.markdown(f"""
                <div style="font-size: 13px; color: #4B5563; padding: 8px 0; border-bottom: 1px solid #F3F4F6;">
                    <strong>{item[1]}</strong>
                    <br>Score: {item[2]}%
                </div>
                """, unsafe_allow_html=True)

    # Main Content
    st.markdown("## Assessment Dashboard")
    st.markdown("<p style='color: #6B7280; margin-bottom: 32px;'>Manage candidate screenings and AI evaluations.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Candidate Resume")
        uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("Document parsed securely.")
        else:
            resume_text = st.text_area("Manual Data Entry", height=200, placeholder="Paste resume text...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Job Requisition")
        job_role = st.text_input("Role Title", placeholder="e.g. Senior Backend Engineer")
        job_desc = st.text_area("Job Description", height=200, placeholder="Enter requirements...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid #E5E7EB; margin: 32px 0;'>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([3, 1])
    with col_r:
        analyze_btn = st.button("Run Evaluation")

    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("Processing analysis..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                # Results
                st.markdown("---")
                
                m1, m2 = st.columns([1, 2])
                with m1:
                    st.markdown('<div class="dashboard-card" style="text-align: center;">', unsafe_allow_html=True)
                    st.markdown("#### Compatibility")
                    color = "#EF4444" if score < 50 else "#10B981"
                    st.markdown(f"<div style='font-size: 48px; font-weight: 700; color: {color};'>{score}%</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with m2:
                    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                    st.markdown("#### AI Assessment Report")
                    st.info(feedback)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please complete all fields.")