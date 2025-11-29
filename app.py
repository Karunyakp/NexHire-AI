import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

st.set_page_config(page_title="NexHire Platinum", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
    }

    .stMarkdown a {
        display: none !important;
        pointer-events: none;
    }
    
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }

    .stApp {
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF;
        border-radius: 12px; 
        border: 1px solid #E5E7EB;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        padding: 32px;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #F9FAFB !important;
        border: 1.5px solid #E5E7EB !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        color: #1F2937 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        background-color: #FFFFFF !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #6366F1 0%, #5B5FE8 100%);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        width: 100%;
        margin-top: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        font-size: 14px;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #5B5FE8 0%, #4F52DF 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.4);
    }
    
    div.stButton > button:active {
        transform: translateY(0);
    }

    h1 {
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0F172A;
        font-size: 2.5rem;
    }
    
    h2 { 
        font-weight: 600; 
        letter-spacing: -0.01em; 
        color: #1F2937;
        font-size: 1.5rem;
    }
    
    h3 { 
        font-size: 1rem; 
        font-weight: 600; 
        color: #374151; 
        margin: 0;
    }
    
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #E5E7EB;
    }
    
    .stTabs [aria-selected="true"] {
        color: #6366F1 !important;
        border-bottom-color: #6366F1 !important;
    }
    
    .stTabs [aria-selected="false"] {
        color: #9CA3AF !important;
    }
    
    div[data-testid="stImage"] > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0F172A;
    }

    /* Fix duplicate password eye and native browser reveal */
    input::-ms-reveal, input::-ms-clear { display: none !important; }
    .stTextInput > div > div > button:first-of-type { display: none !important; }
    .stTextInput > div > div > input[type="password"] ~ button {
        width: 28px !important;
        height: 28px !important;
        padding: 2px !important;
        margin: 0 6px 0 0 !important;
        opacity: 0.95 !important;
    }
    .stTextInput > div > div > input:focus {
        outline: none !important;
        box-shadow: 0 0 0 4px rgba(99,102,241,0.12) !important;
    }
    .stTextInput > div {
        border: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        
        with st.container(border=True):
            logo_c1, logo_c2, logo_c3 = st.columns([1, 2, 1])
            with logo_c2:
                try:
                    st.image("logo.png", use_container_width=True)
                except:
                    st.markdown("<h1 style='text-align: center; color: #6366F1;'>NexHire</h1>", unsafe_allow_html=True)

            st.markdown("<h3 style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>Enterprise Resume Analysis</h3>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<p style='text-align: center; color: #6B7280; font-size: 13px; margin: 20px 0;'>Resume Analysis powered by AI</p>", unsafe_allow_html=True)
            
            tab_sign, tab_reg = st.tabs(["Sign In", "Register"])
            
            with tab_sign:
                st.write("")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Sign In", use_container_width=True):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Access Denied. Invalid credentials.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.write("")
                if st.button("Create Account", use_container_width=True):
                    if new_user and new_pass:
                        if db.add_user(new_user, new_pass):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already taken.")
                    else:
                        st.warning("Please fill in all fields.")

        st.markdown("<p style='text-align: center; margin-top: 20px; color: #9CA3AF; font-size: 12px;'>© 2025 NexHire. Secure & Confidential.</p>", unsafe_allow_html=True)

else:
    c_left, c_right = st.columns([6, 1])
    with c_left:
        cl1, cl2 = st.columns([1, 6])
        with cl1:
            try:
                st.image("logo.png", width=70)
            except:
                st.write("•")
        with cl2:
            st.markdown(f"### Welcome, {st.session_state['username'].title()}")
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Resume Analysis Dashboard</p>", unsafe_allow_html=True)
            
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.divider()

    history = db.fetch_history(st.session_state['username'])
    last_score = history[0][2] if history else 0
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3, gap="large")
    
    with m1:
        with st.container(border=True):
            st.markdown("<div class='metric-label'>Latest Score</div>", unsafe_allow_html=True)
            color = "#10B981" if last_score >= 70 else "#F59E0B" if last_score >= 50 else "#EF4444"
            st.markdown(f"<div class='metric-value' style='color: {color};'>{last_score}%</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #9CA3AF; font-size: 12px; margin: 8px 0 0 0;'>Most recent analysis</p>", unsafe_allow_html=True)
    
    with m2:
        with st.container(border=True):
            st.markdown("<div class='metric-label'>Total Analyses</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value'>{len(history)}</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #9CA3AF; font-size: 12px; margin: 8px 0 0 0;'>Scans completed</p>", unsafe_allow_html=True)
    
    with m3:
        with st.container(border=True):
            st.markdown("<div class='metric-label'>System Status</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value' style='color: #10B981;'>Online</div>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #9CA3AF; font-size: 12px; margin: 8px 0 0 0;'>Operational</p>", unsafe_allow_html=True)

    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        with st.container(border=True):
            st.markdown("<h2 style='margin-bottom: 12px;'>Resume</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B7280; font-size: 13px; margin-bottom: 16px;'>Upload PDF or paste resume text</p>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf", label_visibility="collapsed")
            
            resume_text = ""
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages:
                        resume_text += page.extract_text()
                st.success("Resume extracted successfully")
            else:
                resume_text = st.text_area("Paste resume text", height=180, placeholder="Copy and paste candidate resume here...", label_visibility="collapsed")

    with col_side:
        with st.container(border=True):
            st.markdown("<h2 style='margin-bottom: 12px;'>Job Details</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B7280; font-size: 13px; margin-bottom: 16px;'>Enter position details</p>", unsafe_allow_html=True)
            
            job_role = st.text_input("Position Title", placeholder="Senior Designer", label_visibility="collapsed")
            job_desc = st.text_area("Job Description", height=180, placeholder="Paste job description...", label_visibility="collapsed")

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
    with col_btn_2:
        analyze_btn = st.button("Analyze Resume", type="primary", use_container_width=True)
    
    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("Running analysis..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
            st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
            st.divider()
            
            r1, r2 = st.columns([1, 2])
            with r1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.markdown("<div class='metric-label'>Match Score</div>", unsafe_allow_html=True)
                    color = "#10B981" if score >= 70 else "#F59E0B" if score >= 50 else "#EF4444"
                    st.markdown(f"<div style='font-size: 64px; font-weight: 700; color: {color}; margin: 16px 0;'>{score}%</div>", unsafe_allow_html=True)
                    status = "Excellent" if score >= 70 else "Moderate" if score >= 50 else "Needs Review"
                    st.markdown(f"<p style='color: #6B7280; font-size: 13px;'>{status} Match</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with r2:
                with st.container(border=True):
                    st.markdown("<h3 style='margin-bottom: 16px;'>AI Assessment</h3>", unsafe_allow_html=True)
                    st.markdown(feedback)
        else:
            st.warning("Please fill in all required fields: Resume and Job Description")
