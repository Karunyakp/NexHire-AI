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

# --- CUSTOM CSS FOR MODERN UI ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 8px; }
    .css-1v0mbdj { margin-top: -50px; }
    .metric-card { background-color: #1f2937; padding: 20px; border-radius: 10px; border: 1px solid #374151; }
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
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo.png", width=150) # Ensure you have a logo.png
        st.title("NexHire Login")
        st.write("Welcome back to your AI Career Assistant.")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", type="primary"):
                if username == st.secrets["admin"]["username"] and password == st.secrets["admin"]["password"]:
                    st.session_state['user'] = {'username': 'ADMIN', 'role': 'admin'}
                    st.rerun()
                elif db.verify_user(username, hash_password(password)):
                    st.session_state['user'] = {'username': username, 'role': 'user'}
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account"):
                if db.create_user(new_user, hash_password(new_pass)):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists.")

def dashboard_page():
    user = st.session_state['user']
    
    # Sidebar
    with st.sidebar:
        st.image("logo.png", width=100)
        st.write(f"👤 **{user['username']}**")
        if st.button("Logout"):
            st.session_state['user'] = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📜 History")
        history = db.get_user_history(user['username'])
        for entry in history[-5:]:
            st.caption(f"{entry[3]} - {entry[2]}%")

    # Main Content
    st.title("🚀 Smart Resume Analysis")
    st.markdown("Upload your resume and the job description to get AI-powered insights.")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Your Resume")
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        resume_text = st.text_area("Or Paste Resume Text", height=200)
        
        if uploaded_file:
            resume_text = extract_text_from_pdf(uploaded_file)
            st.success("PDF Loaded Successfully")

    with col2:
        st.subheader("2. Job Description")
        job_desc = st.text_area("Paste Job Description (JD)", height=295)

    if st.button("🔍 Analyze Resume", type="primary"):
        if resume_text and job_desc:
            with st.spinner("AI is analyzing your profile... (This may take 30s)"):
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
        st.markdown("---")
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ATS Score", f"{res['ats']['score']}%", delta_color="normal")
        m2.metric("Role Detected", res['role'])
        m3.metric("AI Probability", f"{res['auth'].get('confidence', 0)}%")
        m4.metric("Status", "Ready" if res['ats']['score'] > 70 else "Needs Work")

        # Tabs for detailed view
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis", "📄 Cover Letter", "🛣️ Roadmap", "🎓 Prep & Practice"])
        
        with tab1:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader("📝 Missing Keywords")
                st.write(res['ats']['missing_keywords'])
                st.subheader("📋 Summary")
                st.write(res['ats']['summary'])
            with c2:
                st.subheader("📈 Market Data")
                st.markdown(res['market'])
        
        with tab2:
            st.subheader("✍️ Generated Cover Letter")
            st.text_area("Copy this:", value=res['cover_letter'], height=400)
            st.download_button("Download Cover Letter", res['cover_letter'], "cover_letter.txt")

        with tab3:
            st.subheader("📅 4-Week Learning Plan")
            st.markdown(res['roadmap'])

        # --- NEW PREP & PRACTICE ZONE (Replaces Recruiter Outreach) ---
        with tab4:
            st.markdown("### 🎓 Prep & Practice Zone")
            st.caption("Tools to help you get ready for the big day.")
            
            pp1, pp2 = st.columns([1, 1])
            
            # --- FEATURE 1: BULLET POINT POLISHER ---
            with pp1:
                with st.container(border=True):
                    st.markdown("#### ✨ Bullet Point Polisher")
                    st.info("Don't just say 'I did java'. Make it shine!")
                    
                    weak_point = st.text_area("Paste a weak resume sentence:", placeholder="e.g. I worked on a python project for class...")
                    
                    if st.button("✨ Polish My Bullet Point"):
                        if weak_point:
                            with st.spinner("Applying STAR Method..."):
                                polished = ai.refine_bullet_point(weak_point, res['role'])
                                st.success("Stronger Version:")
                                st.code(polished, language="text")
                        else:
                            st.warning("Paste some text first!")

            # --- FEATURE 2: MOCK INTERVIEWER ---
            with pp2:
                with st.container(border=True):
                    st.markdown("#### 🤖 AI Mock Interviewer")
                    
                    # Initialize Interview State
                    if 'interview_active' not in st.session_state:
                        st.session_state['interview_active'] = False
                        st.session_state['current_q'] = "Tell me about yourself and your project experience."
                        st.session_state['chat_history'] = []

                    if not st.session_state['interview_active']:
                        if st.button("Start Mock Interview"):
                            st.session_state['interview_active'] = True
                            st.rerun()
                    else:
                        st.markdown(f"**🎙️ AI asks:** {st.session_state['current_q']}")
                        
                        user_ans = st.text_area("Your Answer:", height=100, key="ans_input")
                        
                        if st.button("Submit Answer"):
                            if user_ans:
                                with st.spinner("Analyzing..."):
                                    # Get feedback and next question
                                    response = ai.evaluate_interview_answer(st.session_state['current_q'], user_ans, res['resume_text'])
                                    
                                    # Update Chat History for display
                                    st.session_state['chat_history'].append(f"**You:** {user_ans}")
                                    st.session_state['chat_history'].append(f"**AI:** {response}")
                                    
                                    # Update current question (Basic logic: entire response becomes prompt for user)
                                    st.session_state['current_q'] = response 
                                    st.rerun()
                        
                        if st.button("End Interview"):
                            st.session_state['interview_active'] = False
                            st.session_state['chat_history'] = []
                            st.rerun()

def admin_page():
    st.title("Admin Console")
    if st.button("Back to Login"):
        st.session_state['user'] = None
        st.rerun()
    
    st.write("All User Data:")
    # Fetch all data from DB (Placeholder)
    st.dataframe(db.get_all_users())

# --- MAIN ROUTING ---
if not st.session_state['user']:
    login_page()
else:
    if st.session_state['user']['role'] == 'admin':
        admin_page()
    else:
        dashboard_page()
