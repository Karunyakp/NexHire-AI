import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire Platinum", page_icon="✨", layout="wide")

# --- PLATINUM DESIGN SYSTEM (Unique & Clean) ---
st.markdown("""
    <style>
    /* 1. TYPOGRAPHY: 'Outfit' is distinct and modern */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #111827;
        background-color: #F9FAFB;
    }

    /* 2. BACKGROUND: Clean Canvas (No Grid, No Mess) */
    .stApp {
        background-color: #F9FAFB;
    }

    /* 3. NATIVE CONTAINERS (The "Platinum" Card Look) */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF;
        border-radius: 16px; 
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        padding: 30px;
    }

    /* 4. INPUTS: Clean & Square-ish (Distinct from his rounded pills) */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 8px; /* Sharp corners */
        padding: 14px;
        color: #111827;
        font-size: 15px;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4F46E5; /* Deep Violet */
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }

    /* 5. BUTTONS: Deep Violet (Regal & Serious) */
    div.stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 8px;
        padding: 14px 28px;
        font-weight: 600;
        border: none;
        width: 100%;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
    }

    /* 6. HEADINGS & TEXT */
    h1 {
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #111827;
        font-size: 3rem;
    }
    h2 { font-weight: 600; letter-spacing: -0.02em; color: #374151; }
    h3 { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6B7280; margin-bottom: 8px; }
    
    /* 7. HIDE STREAMLIT UI */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 8. TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #E5E7EB;
    }
    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
        border-bottom-color: #4F46E5 !important;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# ==========================================
# 💎 LOGIN SCREEN (Minimalist Centered)
# ==========================================
if not st.session_state['logged_in']:
    
    # Ratios for perfect center
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        st.write("") 
        
        # NATIVE CONTAINER (Safe & Clean)
        with st.container(border=True):
            # Minimal Logo Area
            st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>NexHire</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #6B7280; font-size: 16px; margin-bottom: 30px;'>The Platinum Standard for Hiring.</p>", unsafe_allow_html=True)
            
            tab_sign, tab_reg = st.tabs(["Sign In", "Register"])
            
            with tab_sign:
                st.write("")
                username = st.text_input("Email Address", key="login_user", placeholder="you@company.com")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Continue to Dashboard"):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Access Denied.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("New Username", key="new_user")
                new_pass = st.text_input("New Password", type="password", key="new_pass")
                st.write("")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        if db.add_user(new_user, new_pass):
                            st.success("Profile created.")
                        else:
                            st.error("Unavailable.")

        # Footer
        st.markdown("<p style='text-align: center; margin-top: 20px; color: #9CA3AF; font-size: 12px;'>© 2025 NexHire Systems Inc. Secure Connection.</p>", unsafe_allow_html=True)

# ==========================================
# 💎 DASHBOARD (Asymmetric Layout - Very Modern)
# ==========================================
else:
    # Top Bar
    c_left, c_right = st.columns([6, 1])
    with c_left:
        st.markdown(f"### Hello, {st.session_state['username']}")
        st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Your analytics overview</p>", unsafe_allow_html=True)
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.divider()

    # Metrics (Clean Cards)
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
    
    # Main Interaction Area
    # We use a 2/3 + 1/3 split for a more "Dashboard" feel than a simple 50/50 split
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

    # Full Width Action Bar
    st.write("")
    if st.button("Initialize Intelligence Engine", type="primary"):
        if resume_text and job_desc:
            with st.spinner("Performing Gap Analysis..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.divider()
                
                # Results (Clean & Sharp)
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