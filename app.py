import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
import advanced_features as af
import PyPDF2
import time
import os
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NexHire", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #111827;
        background-color: #F9FAFB;
    }
    
    .stApp {
        background-color: #F9FAFB;
    }

    /* Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        padding: 32px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700;
        color: #111827;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #6B7280;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }

    /* Hide Footer only, keep header for settings */
    footer {visibility: hidden;}
    
    /* Custom Footer */
    .custom-footer {
        text-align: center;
        color: #6B7280;
        font-size: 12px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #E5E7EB;
    }
    .custom-footer a {
        color: #4F46E5;
        text-decoration: none;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def extract_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in reader.pages])
    except: return None

def render_footer():
    st.markdown("""
        <div class="custom-footer">
            Developed by <b>Karunya. K. P</b> | 
            <a href="https://www.linkedin.com/in/karunya-kp" target="_blank">Connect on LinkedIn</a> | 
            <a href="https://github.com/in/Karunyakp" target="_blank">Connect on Github </a>
            <br>© 2025 NexHire Inc.
        </div>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
def login_page():
    # Render sidebar on login page too
    render_sidebar()
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        with st.container(border=True):
            
            # --- IMAGE LOGO SECTION ---
            c_img1, c_img2, c_img3 = st.columns([1, 1, 1])
            with c_img2:
                if os.path.exists("logo.png"):
                    st.image("logo.png", width=100)
                else:
                    st.header("💼")

            st.markdown("""
                <div style="text-align: center; margin-bottom: 24px; margin-top: 10px;">
                    <h2 style="margin: 0; font-weight: 700; color: #111827; font-size: 24px;">NexHire</h2>
                    <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">Enterprise Recruitment Intelligence</p>
                </div>
            """, unsafe_allow_html=True)
            
            tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])
            
            with tab_login:
                u = st.text_input("Username", key="l_user")
                p = st.text_input("Password", type="password", key="l_pwd")
                if st.button("Sign In", type="primary", use_container_width=True):
                    if ai.validate_admin_login(u, p):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = u
                        st.session_state['role'] = 'Admin'
                        st.session_state['is_guest'] = False
                        st.session_state['admin_unlocked'] = True
                        st.rerun()
                    elif db.login_user(u, p):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = u
                        st.session_state['role'] = 'User'
                        st.session_state['is_guest'] = False
                        st.session_state['admin_unlocked'] = False
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
            
            with tab_reg:
                new_u = st.text_input("Choose Username", key="r_user")
                new_p = st.text_input("Choose Password", type="password", key="r_pwd")
                if st.button("Create Account", use_container_width=True):
                    if len(new_p) < 8: 
                        st.error("Password must be at least 8 characters.")
                    elif db.add_user(new_u, new_p): 
                        st.success("Account created! Please Sign In.")
                    else: 
                        st.error("Username already exists.")

            st.markdown("""
                <div style="text-align: center; margin: 20px 0;">
                    <span style="background-color: white; padding: 0 10px; color: #9CA3AF; font-size: 12px;">OR CONTINUE AS</span>
                </div>
            """, unsafe_allow_html=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("Explore as Candidate", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = "Guest Candidate"
                    st.session_state['role'] = "Candidate"
                    st.session_state['is_guest'] = True
                    st.session_state['admin_unlocked'] = False
                    st.rerun()
            with col_g2:
                if st.button("Explore as Recruiter", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = "Guest Recruiter"
                    st.session_state['role'] = "Recruiter"
                    st.session_state['is_guest'] = True
                    st.session_state['admin_unlocked'] = False
                    st.rerun()
        
        render_footer()

# --- 4. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120) 
        else:
            st.header("NexHire")
        
        # Only show user info if logged in
        if st.session_state.get('logged_in'):
            st.markdown(f"### Hi, {st.session_state.get('username', 'Guest')} 👋")
            st.caption(f"Role: {st.session_state.get('role', 'Viewer')}")
            st.write("")
            if st.button("Sign Out", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        st.divider()
        st.markdown("### Resources")
        
        if st.button("📄 Documentation", use_container_width=True):
            @st.dialog("Documentation")
            def show_docs():
                st.write("**NexHire User Guide**")
                st.write("1. **Candidates**: Upload your resume to check ATS scores and get job fit analysis.")
                st.write("2. **Recruiters**: Upload bulk resumes to screen them against job descriptions.")
                st.write("3. **Security**: All data is processed securely.")
            show_docs()

        if st.button("💬 Support", use_container_width=True):
            @st.dialog("Contact Support")
            def show_support():
                st.write("Need help? Contact our team:")
                st.write(" **Email**: karunyayashu6@gmail.com")
                st.write(" **Phone**: +91 XXXXX XXXXX")
            show_support()
            
        st.markdown("---")
        st.markdown("[🔗 Connect on LinkedIn](https://www.linkedin.com/in/karunya-kp)")
        st.markdown("[💻 Connect on GitHub](https://github.com/in/Karunyakp)")
        st.markdown("---")
        st.markdown("**Developed by**")
        st.markdown("Karunya. K. P")
        st.caption("© 2025 NexHire Inc.")

# --- 5. NEXBOT POPUP COMPONENT ---
def render_nexbot_button(key_suffix="default"):
    with st.popover("💬 Chat with NexBot", use_container_width=False):
        st.markdown("### 🤖 NexBot Assistant")
        st.caption("Ask me anything about your resume or hiring!")
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]

        chat_container = st.container(height=300)
        with chat_container:
            for message in st.session_state.messages:
                # Use chat.png for assistant if available
                avatar = "chat.png" if message["role"] == "assistant" and os.path.exists("chat.png") else None
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        # Use a unique key for the input based on where it's called
        if prompt := st.chat_input("Ask a question...", key=f"chatbot_input_{key_suffix}"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                avatar = "chat.png" if os.path.exists("chat.png") else None
                with st.chat_message("assistant", avatar=avatar):
                    with st.spinner("Thinking..."):
                        response = ai.chat_response(prompt)
                        st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- 6. CANDIDATE MODE ---
def candidate_mode():
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("### 🎓 Candidate Dashboard")
        st.caption("Optimize your profile to get hired faster.")
    with h2:
        render_nexbot_button(key_suffix="candidate")
    
    # --- HISTORY / SAVED PLANS SECTION ---
    try:
        history = db.fetch_user_history(st.session_state['username'])
        saved_plans = [h for h in history if h[3] == "Complete AI Scan"]
        
        if saved_plans:
            with st.expander("📚 Saved Learning Plans & History"):
                for plan in saved_plans:
                    timestamp = plan[0]
                    score = plan[4]
                    details_str = plan[5]
                    try:
                        details = json.loads(details_str)
                        roadmap = details.get('roadmap', 'No roadmap saved.')
                        st.markdown(f"**{timestamp}** - Score: {score}%")
                        if st.button(f"View Plan ({timestamp})", key=f"hist_{timestamp}"):
                            st.info("Re-loaded Plan from History")
                            st.write(roadmap)
                    except: pass
    except Exception as e:
        # Fallback if DB fetch fails
        pass

    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1: 
        input_method = st.radio("Resume Input Method", ["Upload PDF", "Paste Text"], horizontal=True)
        
        resume_text = None
        if input_method == "Upload PDF":
            resume = st.file_uploader("Upload Your Resume (PDF)", type="pdf", key="c_res")
            if resume:
                resume_text = extract_text(resume)
        else:
            resume_text = st.text_area("Paste Resume Content", height=300, key="c_res_text", placeholder="Paste your resume text here...")

    with c2: 
        target_role = st.text_input("Target Job Title", placeholder="e.g. Senior Product Manager")
        jd = st.text_area("Paste Job Description", height=150, key="c_jd", placeholder="Paste the job description you are applying for...")
    
    if resume_text:
        st.write("")
        st.markdown("#### Actions")
        
        col_act1, col_act2, col_act3, col_act4 = st.columns(4)
        
        with col_act1:
            analyze_fit_btn = st.button("🚀 Complete AI Scan", type="primary", use_container_width=True, help="Full analysis against JD")
        with col_act2:
            quick_scan_btn = st.button("⚡ Quick Scan", use_container_width=True, help="Fast resume review without JD")
        with col_act3:
            ats_score_btn = st.button("📊 ATS Score", use_container_width=True)
        with col_act4:
            interview_prep_btn = st.button("🎤 Interview Prep", use_container_width=True)

        # Logic for "Complete AI Scan" (Job Fit)
        if analyze_fit_btn:
             if not jd:
                 st.error("Please provide a Job Description for a Complete AI Scan.")
             else:
                 st.toast("Analyzing... Please wait approx. 2 mins for complete results!", icon="⏳")
                 with st.spinner("Performing Complete AI Scan... (This may take up to 2 minutes)"):
                    text = resume_text
                    # Store Title for PDF
                    st.session_state['c_role_title'] = target_role if target_role else "Target Role"
                    
                    full_jd = f"Target Role: {target_role}\n\n{jd}" if target_role else jd
                    
                    st.session_state['c_data'] = ai.analyze_fit(text, full_jd)
                    st.session_state['c_roadmap'] = ai.get_roadmap(text, full_jd)
                    
                    # Store Analyzed Text (Avoiding widget key conflict)
                    st.session_state['c_text_stored'] = text
                    st.session_state['c_jd_stored'] = full_jd
                    
                    st.session_state['view_mode'] = 'fit'
                    
                    full_details = st.session_state['c_data']
                    full_details['roadmap'] = st.session_state['c_roadmap']
                    
                    db.save_scan(st.session_state['username'], "Candidate", "Complete AI Scan", st.session_state['c_data'].get('score', 0), full_details)

        # Logic for "Quick Scan"
        if quick_scan_btn:
             with st.spinner("Running Quick Resume Scan..."):
                text = resume_text
                cat = ai.categorize_resume(text)
                auth = ai.check_authenticity(text)
                
                # SAFETY FIX: Check if auth is None (API failure)
                if auth is None:
                    auth = {'human_score': 0, 'verdict': 'Error (API)', 'analysis': 'Could not analyze.'}
                
                st.session_state['c_quick'] = {'category': cat, 'auth': auth}
                st.session_state['c_text_stored'] = text
                st.session_state['view_mode'] = 'quick'
                
                db.save_scan(st.session_state['username'], "Candidate", "Quick Scan", auth.get('human_score', 0), auth)

        # Logic for "ATS Score"
        if ats_score_btn:
             if not jd:
                 st.error("Job Description is recommended for accurate ATS scoring.")
             else:
                 with st.spinner("Calculating ATS score..."):
                    text = resume_text
                    full_jd = f"Target Role: {target_role}\n\n{jd}" if target_role else jd
                    
                    st.session_state['c_ats_data'] = ai.run_screening(text, full_jd) 
                    st.session_state['c_text_stored'] = text
                    st.session_state['c_jd_stored'] = full_jd
                    st.session_state['view_mode'] = 'ats'

        # Logic for "Interview Prep"
        if interview_prep_btn:
             if not jd:
                 st.error("Job Description required for tailored interview questions.")
             else:
                 with st.spinner("Generating interview questions..."):
                    text = resume_text
                    full_jd = f"Target Role: {target_role}\n\n{jd}" if target_role else jd
                    
                    st.session_state['c_interview'] = ai.get_interview_prep(text, full_jd)
                    st.session_state['c_text_stored'] = text
                    st.session_state['c_jd_stored'] = full_jd
                    st.session_state['view_mode'] = 'interview'

    # DISPLAY RESULTS
    if 'view_mode' in st.session_state:
        st.divider()
        
        # 1. COMPLETE AI SCAN (JOB FIT & ROADMAP)
        if st.session_state['view_mode'] == 'fit' and 'c_data' in st.session_state:
            data = st.session_state['c_data']
            c_score, c_text = st.columns([1, 3])
            with c_score: st.metric("Overall Match", f"{data['score']}%")
            with c_text: 
                st.info(f"**Summary:** {data['summary']}")
            
            st.subheader("Skills Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("✅ **Matched**")
                for s in data['skills']['matched']: st.success(s)
            with col2:
                st.markdown("⚠️ **Partial**")
                for s in data['skills']['partial']: st.warning(s)
            with col3:
                st.markdown("❌ **Missing**")
                for s in data['skills']['missing']: st.error(s)

            with st.expander("📅 4-Week Improvement Plan (Timetable)", expanded=True):
                 roadmap = st.session_state.get('c_roadmap', "Roadmap generation failed. Please try again.")
                 st.write(roadmap)
            
            # --- PDF DOWNLOAD BUTTON ---
            if st.button("📥 Download Report (PDF)"):
                try:
                    # Pass only the ROLE TITLE, not the full JD
                    role_title = st.session_state.get('c_role_title', 'Target Role')
                    
                    pdf_bytes = af.generate_pdf_report(
                        st.session_state['username'],
                        role_title, # FIXED: Uses short title
                        data['score'],
                        data['summary'] + "\n\nROADMAP:\n" + roadmap,
                        ", ".join(data['skills']['matched']),
                        ", ".join(data['skills']['missing']),
                        "General"
                    )
                    st.download_button(
                        label="Click to Download PDF",
                        data=pdf_bytes,
                        file_name="NexHire_Report.pdf",
                        mime="application/pdf",
                        key="dl_pdf_btn"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")

        # 2. QUICK SCAN
        elif st.session_state['view_mode'] == 'quick' and 'c_quick' in st.session_state:
            res = st.session_state['c_quick']
            st.subheader("Quick Scan Results")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Detected Category", res['category'])
            with c2:
                auth = res['auth']
                # Added safety check for None auth here as well if needed
                score = auth.get('human_score', 0) if auth else 0
                verdict = auth.get('verdict', 'Unknown') if auth else 'Unknown'
                st.metric("Authenticity Score", f"{score}%")
                st.caption(f"Verdict: {verdict}")
            
            st.info("For a detailed analysis against a specific job, use 'Complete AI Scan'.")

        # 3. ATS SCORE
        elif st.session_state['view_mode'] == 'ats' and 'c_ats_data' in st.session_state:
            data = st.session_state['c_ats_data']
            st.subheader("ATS Compatibility")
            m1, m2 = st.columns(2)
            with m1: st.metric("ATS Parse Score", f"{data['ats_score']}%")
            with m2: 
                if data['ats_score'] > 80: st.success("Highly Readable")
                elif data['ats_score'] > 50: st.warning("Needs Formatting Fixes")
                else: st.error("Risk of Rejection")
            st.write(data['summary'])

        # 4. INTERVIEW PREP
        elif st.session_state['view_mode'] == 'interview' and 'c_interview' in st.session_state:
            st.subheader("🎤 Interview Preparation")
            st.write(st.session_state['c_interview'])

# --- 7. RECRUITER MODE ---
def recruiter_mode():
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("### 🧑‍💼 Recruiter Workspace")
        st.caption("Bulk screen candidates and identify top talent instantly.")
    with h2:
        render_nexbot_button(key_suffix="recruiter")

    c1, c2 = st.columns([1, 1])
    with c1: 
        resumes = st.file_uploader("Upload Resumes (PDF)", type="pdf", key="r_res", accept_multiple_files=True)
    with c2: 
        job_title = st.text_input("Job Position Title", placeholder="e.g. Senior Data Scientist")
        jd = st.text_area("Job Requirements", height=150, key="r_jd")
    
    bias_free = st.toggle("Enable Bias-Free Screening (Hide Name/Gender)")
    
    if st.button("Run Bulk Screening", type="primary"):
        if resumes and jd:
            results_list = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_files = len(resumes)
            
            full_jd = f"Target Role: {job_title}\n\n{jd}" if job_title else jd
            
            for i, res in enumerate(resumes):
                status_text.text(f"Processing {res.name} ({i+1}/{total_files})...")
                text = extract_text(res)
                if text:
                    ai_data = ai.run_screening(text, full_jd, bias_free)
                    results_list.append({
                        "Filename": res.name,
                        "ATS Score": ai_data.get('ats_score', 0),
                        "Authenticity": ai_data.get('auth_badge', 'Unknown'),
                        "Red Flags": len(ai_data.get('red_flags', [])),
                        "Summary": ai_data.get('summary', 'No summary provided')
                    })
                    db.save_scan(st.session_state['username'], "Recruiter", f"Bulk: {res.name}", ai_data.get('ats_score', 0), ai_data)
                progress_bar.progress((i + 1) / total_files)
                
            st.session_state['r_bulk_data'] = results_list
            status_text.text("Screening Complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
        elif not resumes: st.error("Please upload at least one resume.")
        elif not jd: st.error("Please provide a job description.")

    if 'r_bulk_data' in st.session_state and st.session_state['r_bulk_data']:
        st.divider()
        st.subheader("Screening Results")
        
        df_results = pd.DataFrame(st.session_state['r_bulk_data'])
        df_results = df_results.sort_values(by="ATS Score", ascending=False).reset_index(drop=True)
        
        st.dataframe(
            df_results,
            column_config={
                "ATS Score": st.column_config.ProgressColumn("Match Score", format="%d%%", min_value=0, max_value=100),
                "Authenticity": st.column_config.TextColumn("Authenticity Badge"),
            },
            use_container_width=True
        )
        
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results CSV", csv, "screening_results.csv", "text/csv")

# --- 8. ADMIN CONSOLE ---
def admin_console():
    st.markdown("### System Administration")
    data = db.get_all_full_analysis()
    if data:
        df = pd.DataFrame(data, columns=["Timestamp", "Username", "Mode", "Action", "Score", "Details"])
        st.dataframe(df, use_container_width=True)
    else: st.info("No system activity recorded.")

# --- 9. MAIN APP LOGIC ---
def main():
    # Force table creation at startup
    db.create_tables()
    
    if not st.session_state.get('logged_in'):
        login_page()
    else:
        render_sidebar()
        
        if st.session_state.get('admin_unlocked'):
            admin_console()
        else:
            role = st.session_state.get('role', 'User')
            
            if role == "Candidate":
                candidate_mode()
            elif role == "Recruiter":
                recruiter_mode()
            else:
                # Fallback for generic user
                tab1, tab2 = st.tabs(["Candidate Tools", "Recruiter Tools"])
                with tab1: candidate_mode()
                with tab2: recruiter_mode()
        
        # Render footer in dashboard mode as well
        render_footer()

if __name__ == "__main__":
    main()
