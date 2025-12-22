import streamlit as st
import database as db
import ai_engine as ai
import advanced_features as af
import hashlib
import time
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NexHire: AI Resume Architect",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NEW MODERN UI (PATTERNED BACKGROUND) ---
st.markdown("""
<style>
    /* 1. Main Background - Tech Grid Pattern */
    .stApp {
        background-color: #f8f9fa;
        opacity: 1;
        background-image:  radial-gradient(#d1d5db 0.5px, transparent 0.5px), radial-gradient(#d1d5db 0.5px, #f8f9fa 0.5px);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        color: #2c3e50;
    }

    /* 2. Sidebar - Clean White with Border */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }

    /* 3. Containers/Cards - Glass Effect with Shadow */
    .stTextArea, .stTextInput, .stFileUploader, div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* 4. Buttons - Professional Blue Gradient */
    .stButton>button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        height: 48px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(42, 82, 152, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(42, 82, 152, 0.3);
        color: #ffffff;
    }

    /* 5. Metrics - Floating Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f1f3f5;
    }
    
    /* 6. Tabs - Better spacing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #495057;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd;
        color: #1565c0;
    }

    /* Headings */
    h1, h2, h3 {
        color: #1a252f;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Image centering */
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None

# --- HELPER FUNCTIONS ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- PAGES ---

def login_page():
    # Centered Layout for Login
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        # Display Logo (Ensure logo.png is in the folder)
        try:
            st.image("logo.png", width=250) # Increased logo size significantly
        except:
            st.title("🚀") # Fallback if logo missing
            
        st.markdown("<h1 style='text-align: center;'>NexHire</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d;'>AI-Powered Career Acceleration Platform</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.button("Access Dashboard", type="primary"):
                    if username == st.secrets["admin"]["username"] and password == st.secrets["admin"]["password"]:
                        st.session_state['user'] = {'username': 'ADMIN', 'role': 'admin'}
                        st.rerun()
                    elif db.verify_user(username, hash_password(password)):
                        st.session_state['user'] = {'username': username, 'role': 'user'}
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

            with tab2:
                new_user = st.text_input("Choose Username", key="reg_user")
                new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
                if st.button("Create Account"):
                    if db.create_user(new_user, hash_password(new_pass)):
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username already exists.")

def dashboard_page():
    user = st.session_state['user']
    
    # Sidebar
    with st.sidebar:
        try:
            st.image("logo.png", width=150) # Increased sidebar logo size
        except:
            pass
            
        st.markdown(f"<h3 style='text-align: center;'>Hello, {user['username']}</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation / History
        st.markdown("### 📜 Recent Scans")
        history = db.get_user_history(user['username'])
        if not history:
            st.info("No scans yet.")
        for entry in history[-5:]:
            st.text(f"{entry[3]} - {entry[2]}%")
            
        st.markdown("---")
        if st.button("Logout"):
            st.session_state['user'] = None
            st.rerun()

    # Main Content
    st.title("🚀 Career Dashboard")
    st.markdown("Optimize your resume and prepare for interviews with AI.")
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. Upload Resume")
            uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
            resume_text = st.text_area("Or Paste Text", height=200, placeholder="Paste your resume content here if you don't have a PDF...")
            
            if uploaded_file:
                resume_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF Loaded")

        with col2:
            st.subheader("2. Job Description")
            job_desc = st.text_area("Paste JD", height=295, placeholder="Paste the Job Description here...")

        if st.button("✨ Analyze Profile & Generate Insights", type="primary"):
            if resume_text and job_desc:
                with st.spinner("🤖 AI is analyzing your profile against the market..."):
                    # 1. Basic Scan
                    ats_result = ai.get_ats_score(resume_text, job_desc)
                    
                    # 2. AI Detection
                    authenticity = ai.check_resume_authenticity(resume_text)
                    
                    # 3. Categorization
                    job_role = ai.categorize_resume(resume_text)
                    
                    # 4. Advanced Generation (Parallel calls simulated)
                    cover_letter = ai.generate_cover_letter(resume_text, job_desc)
                    interview_q = ai.generate_interview_questions(resume_text, job_desc)
                    market_data = ai.get_market_analysis(job_role)
                    roadmap = ai.generate_learning_roadmap(ats_result['missing_keywords'], job_role)
                    
                    # Store in session
                    st.session_state['analysis_result'] = {
                        "ats": ats_result,
                        "auth": authenticity,
                        "role": job_role,
                        "cover_letter": cover_letter,
                        "interview": interview_q,
                        "market": market_data,
                        "roadmap": roadmap,
                        "resume_text": resume_text, # Save for prep tools
                        "job_desc": job_desc
                    }
                    
                    # Save to DB
                    db.save_analysis(user['username'], job_role, ats_result['score'], str(ats_result))
                    st.rerun()
            else:
                st.warning("Please provide both Resume and JD.")

    # --- RESULTS DASHBOARD ---
    res = st.session_state['analysis_result']
    if res:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ATS Match Score", f"{res['ats']['score']}%", delta_color="normal")
        m2.metric("Target Role", res['role'])
        m3.metric("AI Probability", f"{res['auth'].get('confidence', 0)}%")
        m4.metric("Readiness", "High" if res['ats']['score'] > 70 else "Improve")

        st.markdown("---")

        # Tabs for detailed view
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "📄 Cover Letter", "🛣️ Roadmap", "🎓 Prep & Practice"])
        
        with tab1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("📝 Missing Keywords")
                st.info(f"Add these to your resume: {', '.join(res['ats']['missing_keywords'])}")
                st.subheader("📋 Executive Summary")
                st.write(res['ats']['summary'])
            with c2:
                st.subheader("📈 Market Trends")
                st.markdown(res['market'])
        
        with tab2:
            st.subheader("✍️ Tailored Cover Letter")
            st.text_area("Generated Draft:", value=res['cover_letter'], height=400)
            st.download_button("Download .txt", res['cover_letter'], "cover_letter.txt")

        with tab3:
            st.subheader("📅 4-Week Skill-Up Roadmap")
            st.markdown(res['roadmap'])

        # --- PREP & PRACTICE ZONE ---
        with tab4:
            st.markdown("### 🎓 Prep & Practice Zone")
            
            pp1, pp2 = st.columns([1, 1])
            
            # --- FEATURE 1: BULLET POINT POLISHER ---
            with pp1:
                with st.container(border=True):
                    st.markdown("#### ✨ Bullet Point Polisher")
                    st.caption("Turn weak points into 'STAR' achievements.")
                    
                    weak_point = st.text_area("Paste a resume sentence:", placeholder="e.g. I helped make the website faster...")
                    
                    if st.button("✨ Enhance Text"):
                        if weak_point:
                            with st.spinner("Polishing..."):
                                polished = ai.refine_bullet_point(weak_point, res['role'])
                                st.success("Here is a stronger version:")
                                st.code(polished, language="text")
                        else:
                            st.warning("Paste text first!")

            # --- FEATURE 2: MOCK INTERVIEWER ---
            with pp2:
                with st.container(border=True):
                    st.markdown("#### 🤖 AI Mock Interview")
                    st.caption("Live practice for technical questions.")
                    
                    # Initialize Interview State
                    if 'interview_active' not in st.session_state:
                        st.session_state['interview_active'] = False
                        st.session_state['current_q'] = "Tell me about yourself and your project experience."
                        st.session_state['chat_history'] = []

                    if not st.session_state['interview_active']:
                        if st.button("Start Interview Session"):
                            st.session_state['interview_active'] = True
                            st.rerun()
                    else:
                        st.info(f"🎙️ **AI asks:** {st.session_state['current_q']}")
                        
                        user_ans = st.text_area("Your Answer:", height=100, key="ans_input")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Submit Answer"):
                                if user_ans:
                                    with st.spinner("Analyzing..."):
                                        response = ai.evaluate_interview_answer(st.session_state['current_q'], user_ans, res['resume_text'])
                                        st.session_state['chat_history'].append(f"**You:** {user_ans}")
                                        st.session_state['chat_history'].append(f"**AI:** {response}")
                                        st.session_state['current_q'] = response 
                                        st.rerun()
                        with col_b:
                            if st.button("End Session"):
                                st.session_state['interview_active'] = False
                                st.session_state['chat_history'] = []
                                st.rerun()

def admin_page():
    st.title("Admin Console")
    if st.button("Back to Login"):
        st.session_state['user'] = None
        st.rerun()
    
    st.write("All User Data:")
    st.dataframe(db.get_all_users())

# --- MAIN ROUTING ---
if not st.session_state['user']:
    login_page()
else:
    if st.session_state['user']['role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
