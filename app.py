import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire AI", page_icon="⚡", layout="wide")

# --- DARK MODE DESIGN SYSTEM ---
st.markdown("""
    <style>
    /* 1. IMPORT MODERN FONT */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #FFFFFF;
    }
    
    /* 2. BACKGROUND (Deep Space Dark) */
    .stApp {
        background: #0B0E14;
        background-image: radial-gradient(circle at 50% 0%, #1c2333 0%, #0B0E14 70%);
    }
    
    /* 3. HIDE JUNK */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 4. CARDS (The Dark Glass Look) */
    .tech-card {
        background: #151921;
        border: 1px solid #2D3342;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .tech-card:hover {
        border-color: #4F8BF9;
        box-shadow: 0 0 15px rgba(79, 139, 249, 0.2);
    }
    
    /* 5. INPUT FIELDS (Dark Grey, No White) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0B0E14;
        color: #FFFFFF;
        border: 1px solid #2D3342;
        border-radius: 10px;
        padding: 12px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4F8BF9;
        box-shadow: 0 0 0 2px rgba(79, 139, 249, 0.3);
    }
    
    /* 6. BUTTONS (Neon Glow) */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563EB 0%, #9333EA 100%);
        color: white;
        border: none;
        padding: 14px;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
    }
    
    /* 7. TEXT STYLES */
    h1 {
        background: linear-gradient(90deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    h2, h3 { color: #E2E8F0; }
    p, label { color: #94A3B8 !important; }
    
    /* 8. TABS */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #2D3342; }
    .stTabs [aria-selected="true"] { color: #4F8BF9 !important; border-bottom-color: #4F8BF9 !important; }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# ==========================================
# 🌑 LOGIN SCREEN (DARK MODE)
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        
        # Logo Area
        st.markdown("<h1 style='text-align: center; font-size: 36px; margin-bottom: 5px;'>⚡ NexHire</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px;'>AI-Powered Resume Architect</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["LOG IN", "SIGN UP"])
        
        with tab1:
            st.write("")
            username = st.text_input("Username", key="login_user", placeholder="Ex: admin")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••")
            st.write("")
            if st.button("Initialize Session"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Access Denied")
        
        with tab2:
            st.write("")
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            st.write("")
            if st.button("Create ID"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.success("ID Created. Proceed to Login.")
                    else:
                        st.error("Username Unavailable")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ⚡ DASHBOARD (DARK MODE)
# ==========================================
else:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['username']}")
        st.caption("Pro License Active")
        st.write("")
        if st.button("Terminate Session"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 🕒 Recent Activity")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.markdown(f"""
                <div style="background: #151921; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #2D3342;">
                    <div style="color: #E2E8F0; font-weight: 500; font-size: 13px;">{item[1]}</div>
                    <div style="color: #4F8BF9; font-size: 12px;">Match: {item[2]}%</div>
                </div>
                """, unsafe_allow_html=True)

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Command Center")
        st.markdown("<p>Analyze compatibility and optimize for ATS algorithms.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 📄 Resume Data")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("File Decrypted Successfully")
        else:
            resume_text = st.text_area("Manual Input", height=200, placeholder="Paste resume content...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Target Parameters")
        job_role = st.text_input("Role", placeholder="e.g. Machine Learning Engineer")
        job_desc = st.text_area("Description", height=200, placeholder="Paste job requirements...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #2D3342;'>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn2:
        analyze_btn = st.button("⚡ RUN DIAGNOSTICS")

    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("Processing Neural Network..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                # Results UI
                st.markdown("---")
                
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    st.markdown('<div class="tech-card" style="text-align: center; border-color: #4F8BF9;">', unsafe_allow_html=True)
                    st.markdown("### Match Index")
                    color = "#EF4444" if score < 50 else "#10B981"
                    st.markdown(f"<h1 style='font-size: 60px; color: {color}; margin: 0;'>{score}%</h1>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with c2:
                    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                    st.markdown("### AI Report")
                    st.info(feedback)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Data Missing.")