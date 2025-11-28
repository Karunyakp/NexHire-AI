import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- PAGE CONFIGURATION ---
# Set the page title and layout. No emojis here.
st.set_page_config(page_title="NexHire AI Enterprise", layout="wide")

# --- AESTHETIC PROFESSIONAL CSS DESIGN ---
st.markdown("""
    <style>
    /* Import a professional, modern sans-serif font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Apply the font to the entire app */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b; /* Dark blue-grey text for better readability */
    }
    
    /* --- BACKGROUND IMAGE SECTION --- */
    /* Use a high-quality, subtle professional background image */
    .stApp {
        /* Example professional background image from Unsplash */
        background-image: url('https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2301&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    /* Add a subtle overlay to ensure text readability */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.8); /* Light overlay */
        z-index: -1;
    }
    
    /* --- HIDE DEFAULT STREAMLIT ELEMENTS --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* --- AESTHETIC CARD DESIGN (Glassmorphism) --- */
    .aesthetic-card {
        background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent white */
        backdrop-filter: blur(10px); /* Blur effect for the background */
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        margin-bottom: 24px;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .aesthetic-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
    }
    
    /* --- INPUT FIELDS STYLING --- */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.9);
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 15px;
        transition: border-color 0.2s;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #2563eb; /* Professional blue focus color */
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* --- BUTTON STYLING --- */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); /* Professional blue gradient */
        color: white;
        border: none;
        padding: 14px 20px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        letter-spacing: 0.5px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.95;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    /* --- TYPOGRAPHY STYLES --- */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    h1 { font-size: 2.5rem; }
    h2 { font-size: 1.8rem; }
    h3 { font-size: 1.3rem; margin-bottom: 1rem; }
    p, label { color: #475569; font-size: 1rem; }
    
    /* --- TAB STYLING --- */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #64748b;
        padding-bottom: 12px;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Database and Session State
db.create_tables()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""

# ==========================================
# 🔒 LOGIN SCREEN (PROFESSIONAL)
# ==========================================
if not st.session_state['logged_in']:
    # Center the login card
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True) # Top spacer
        st.markdown('<div class="aesthetic-card">', unsafe_allow_html=True)
        
        # Header without emojis
        st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>NexHire AI Enterprise</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; margin-bottom: 30px; font-size: 1.1rem;'>Intelligent Resume Analysis Platform</p>", unsafe_allow_html=True)
        
        # Tabs for Login/Signup
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            st.write("")
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            st.write("")
            if st.button("Sign In"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        with tab2:
            st.write("")
            new_user = st.text_input("New Username", key="new_user", placeholder="Choose a username")
            new_pass = st.text_input("New Password", type="password", key="new_pass", placeholder="Choose a password")
            st.write("")
            if st.button("Sign Up"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.success("Account created successfully. Please log in.")
                    else:
                        st.error("Username already exists.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 📊 DASHBOARD (PROFESSIONAL)
# ==========================================
else:
    # Sidebar styling
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state['username']}")
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.markdown("### Analysis History")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.8); padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #e2e8f0;">
                    <div style="font-weight: 600; color: #1e293b; font-size: 14px;">{item[1]}</div>
                    <div style="color: #2563eb; font-size: 13px; margin-top: 4px;">Match Score: {item[2]}%</div>
                    <div style="color: #94a3b8; font-size: 11px; margin-top: 4px;">{item[3][:10]}</div>
                </div>
                """, unsafe_allow_html=True)

    # Main content header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Analysis Dashboard")
        st.markdown("<p style='font-size: 1.1rem;'>Upload a resume and job description for AI-powered insights.</p>", unsafe_allow_html=True)

    # Input sections using aesthetic cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="aesthetic-card">', unsafe_allow_html=True)
        st.markdown("### Resume Document")
        uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            with st.spinner("Processing document..."):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    resume_text += page.extract_text()
            st.success("Document processed successfully.")
        else:
            resume_text = st.text_area("Paste Resume Text", height=250, placeholder="Or paste resume content here...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="aesthetic-card">', unsafe_allow_html=True)
        st.markdown("### Job Description")
        job_role = st.text_input("Job Title / Role", placeholder="e.g., Senior Software Engineer")
        job_desc = st.text_area("Paste Job Description", height=250, placeholder="Paste the full job description here...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #e2e8f0; opacity: 0.5; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Analyze Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        analyze_btn = st.button("Run AI Analysis")

    # Results Section
    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("Performing comprehensive analysis..."):
                time.sleep(1) # UX pause
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.markdown("---")
                
                c1, c2 = st.columns([1, 2])
                
                # Score Card
                with c1:
                    st.markdown('<div class="aesthetic-card" style="text-align: center;">', unsafe_allow_html=True)
                    st.markdown("### Match Score")
                    # Determine color based on score
                    score_color = "#ef4444" if score < 50 else ("#f59e0b" if score < 75 else "#10b981")
                    st.markdown(f"<h1 style='font-size: 72px; color: {score_color}; margin: 0;'>{score}%</h1>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: {score_color}; font-weight: 600;'>{'Needs Improvement' if score < 50 else ('Good Match' if score < 75 else 'Excellent Match')}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Feedback Card
                with c2:
                    st.markdown('<div class="aesthetic-card">', unsafe_allow_html=True)
                    st.markdown("### AI Assessment & Feedback")
                    st.write(feedback)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Please provide both a resume and a job description to proceed.")