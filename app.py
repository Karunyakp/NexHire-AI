import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time
from PIL import Image # Needed to load your local image

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire Platinum", page_icon="💜", layout="wide")

# --- PLATINUM DESIGN SYSTEM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #111827;
        background-color: #F9FAFB;
    }

    .stApp {
        background-color: #F9FAFB;
    }

    /* CARD STYLING */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF;
        border-radius: 16px; 
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 30px;
    }

    /* INPUTS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 14px;
        color: #111827;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    /* BUTTONS */
    div.stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 14px 28px;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #E5E7EB; }
    .stTabs [aria-selected="true"] { color: #4F46E5 !important; border-bottom-color: #4F46E5 !important; }
    
    /* CENTER IMAGES */
    div[data-testid="stImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# ==========================================
# 💎 LOGIN SCREEN (With YOUR Custom Logo)
# ==========================================
if not st.session_state['logged_in']:
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        
        with st.container(border=True):
            # --- YOUR LOGO HERE ---
            try:
                # Displays logo.png centered
                st.image("logo.png", width=150) 
            except:
                st.warning("⚠️ Upload 'logo.png' to GitHub to see the image here.")

            st.markdown("<h3 style='text-align: center; color: #6B7280; margin-top: 10px;'>Enterprise Recruitment Intelligence</h3>", unsafe_allow_html=True)
            
            tab_sign, tab_reg = st.tabs(["Sign In", "Register"])
            
            with tab_sign:
                st.write("")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Access Dashboard"):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Access Denied.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.write("")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        if db.add_user(new_user, new_pass):
                            st.success("Success. Please Log In.")
                        else:
                            st.error("Username taken.")

        st.markdown("<p style='text-align: center; margin-top: 20px; color: #9CA3AF; font-size: 12px;'>© 2025 NexHire Systems. Secure.</p>", unsafe_allow_html=True)

# ==========================================
# 💎 DASHBOARD (Logo in Header)
# ==========================================
else:
    # Top Bar with Logo
    c_left, c_right = st.columns([6, 1])
    with c_left:
        # Layout: Logo | Welcome Text
        cl1, cl2 = st.columns([0.8, 5.2])
        with cl1:
            try:
                st.image("logo.png", width=60)
            except:
                st.write("🔹")
        with cl2:
            st.markdown(f"### Hello, {st.session_state['username']}")
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Your analytics overview</p>", unsafe_allow_html=True)
            
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
            st.info("Upload the candidate's PDF resume here.")
            uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
            
            resume_text = ""
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages:
                        resume_text += page.extract_text()
                st.success("Resume Extracted")
            else:
                resume_text = st.text_area("Or paste raw text", height=200, placeholder="Paste resume content here...")

    with col_side:
        with st.container(border=True):
            st.markdown("### 2. Job Requisition")
            job_role = st.text_input("Role Title", placeholder="Product Designer")
            job_desc = st.text_area("Requirements", height=250, placeholder="Paste JD here...", label_visibility="collapsed")

    st.write("")
    if st.button("Initialize Intelligence Engine", type="primary"):
        if resume_text and job_desc:
            with st.spinner("Performing Gap Analysis..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.divider()
                
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
                        st.write(feedback)
        else:
            st.warning("Input required.")