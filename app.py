import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

st.set_page_config(page_title="NexHire AI", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .login-container {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .title-text {
        font-family: 'Arial', sans-serif;
        color: #4F8BF9;
        font-weight: 800;
        font-size: 3rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F8BF9;
        color: white;
        border-radius: 5px;
        height: 50px;
        font-size: 18px;
    }
    .stButton>button:hover {
        background-color: #3b71ca;
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if not st.session_state['logged_in']:
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<p class="title-text">⚡ NexHire AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">The Future of Resume Optimization</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Create Account"])
        
        with tab1:
            st.write("Welcome back!")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")
        
        with tab2:
            st.write("New here? Join us today.")
            new_user = st.text_input("Choose a Username", key="new_user")
            new_pass = st.text_input("Choose a Password", type="password", key="new_pass")
            
            if st.button("Sign Up"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.balloons()
                        st.success("🎉 Account Created Successfully!")
                        st.info("👉 Please switch to the **Login** tab to sign in.")
                    else:
                        st.error("⚠️ Username already taken. Try another.")
                else:
                    st.warning("Please fill in both fields.")

else:
    with st.sidebar:
        st.title(f"👤 {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.markdown("---")
        st.subheader("📜 Scan History")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.caption(f"📅 {item[3][:10]}")
                st.text(f"{item[1]}: {item[2]}%")
                st.markdown("---")
        else:
            st.caption("No scans yet.")

    st.title("⚡ NexHire AI Dashboard")
    st.markdown("### Optimize your resume for the 2025 Job Market.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.container(border=True)
        st.subheader("1. Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        resume_text = ""
        
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("✅ PDF Loaded Successfully")
        else:
            resume_text = st.text_area("Or paste text here", height=200)

    with col2:
        st.container(border=True)
        st.subheader("2. Target Job")
        job_role = st.text_input("Job Role (e.g. Data Scientist)")
        job_desc = st.text_area("Paste Job Description", height=200)

    st.markdown("---")
    center_col1, center_col2, center_col3 = st.columns([1, 2, 1])
    with center_col2:
        analyze_btn = st.button("🚀 Analyze Compatibility", type="primary", use_container_width=True)

    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("NexHire AI is analyzing your profile..."):
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.markdown(f"<h2 style='text-align: center;'>Match Score: {score}%</h2>", unsafe_allow_html=True)
                st.progress(score/100)
                
                if score < 60:
                    st.error("⚠️ Critical Mismatch: High chance of ATS Rejection.")
                elif score < 80:
                    st.warning("⚠️ Good, but needs optimization.")
                else:
                    st.success("✅ Excellent Match!")
                
                with st.expander("💡 See AI Feedback", expanded=True):
                    st.info(feedback)
        else:
            st.warning("Please provide both a Resume and a Job Description.")