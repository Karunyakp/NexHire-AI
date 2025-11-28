import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

st.set_page_config(page_title="NexHire AI", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #4F8BF9 0%, #9B72F2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }

    h1, h2, h3 {
        color: #1E293B;
        font-weight: 700;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>⚡ NexHire AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>The Ultimate Resume Optimizer</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            st.write("")
            if st.button("Access Dashboard"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with tab2:
            new_user = st.text_input("Choose Username", key="new_user")
            new_pass = st.text_input("Choose Password", type="password", key="new_pass")
            st.write("")
            if st.button("Create Account"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.balloons()
                        st.success("Account Created! Switch to Login tab.")
                    else:
                        st.error("Username taken.")
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state['username']}")
        if st.button("Logout", type="secondary"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📜 Recent Activity")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.markdown(f"""
                <div style="padding: 10px; background: white; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #4F8BF9;">
                    <div style="font-weight: bold; font-size: 0.9rem;">{item[1]}</div>
                    <div style="font-size: 0.8rem; color: #666;">Match: {item[2]}%</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.title("🚀 Resume Operations Center")
    st.markdown("Upload your resume and job description to get AI-powered insights.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📄 Candidate Profile")
        uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("PDF Uploaded Successfully")
        else:
            resume_text = st.text_area("Or paste resume text", height=200, placeholder="Paste resume content here...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Target Role")
        job_role = st.text_input("Job Title", placeholder="e.g. Senior React Developer")
        job_desc = st.text_area("Job Description", height=200, placeholder="Paste the JD here...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="text-align: center; margin-top: 20px;">', unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Launch AI Analysis")
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("🤖 AI is reading your resume..."):
                time.sleep(1)
                
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.markdown("---")
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
                        <div style="text-align: center;">
                            <h2 style="margin:0; font-size: 4rem; color: {'#ef4444' if score < 50 else '#22c55e'};">{score}%</h2>
                            <p style="color: #64748B;">Match Score</p>
                        </div>
                        <div style="height: 80px; width: 2px; background: #ddd;"></div>
                        <div style="width: 60%;">
                             <h3>AI Verdict</h3>
                             <p>{'Your resume needs significant work to pass the ATS.' if score < 50 else 'Excellent work! You are likely to get an interview.'}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(score/100)
                st.markdown("### 💡 Strategic Feedback")
                st.info(feedback)
                st.markdown('</div>', unsafe_allow_html=True)
                
        else:
            st.warning("⚠️ Please provide both Resume and Job Description")