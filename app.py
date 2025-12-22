import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
import advanced_features as af
import PyPDF2
import time

def setup_page():
    st.set_page_config(page_title="NexHire Platinum", page_icon="💜", layout="wide")
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            color: #111827;
            background-color: #F9FAFB;
        }
        .stMarkdown a {
            text-decoration: none;
            color: #4F46E5 !important;
            font-weight: 600;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: #FFFFFF;
            border-radius: 16px; 
            border: 1px solid #E5E7EB;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            padding: 40px;
        }
        .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #E5E7EB; }
        .stTabs [aria-selected="true"] { color: #4F46E5 !important; border-bottom-color: #4F46E5 !important; }
        .skill-tag {
            display: inline-block;
            padding: 5px 12px;
            margin: 4px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .skill-match { background-color: #D1FAE5; color: #065F46; border: 1px solid #34D399; }
        .skill-missing { background-color: #FEE2E2; color: #991B1B; border: 1px solid #F87171; }
        .category-badge {
            background-color: #EEF2FF;
            color: #4F46E5;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 14px;
            border: 1px solid #C7D2FE;
        }
        #MainMenu, footer, header {visibility: hidden;}
        div[data-testid="stHeaderActionElements"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        # App Logo (Top)
        try: st.image("logo.png", width=150) 
        except: pass 
        st.title("NexHire")
        st.markdown("### Enterprise Recruitment Intelligence")
        
        # --- CHATBOT SECTION START ---
        st.divider()
        
        # Header with your "chat.png" icon
        c_icon, c_title = st.columns([1, 3])
        with c_icon:
            try: st.image("chat.png", width=60) # Using your specific chat icon here
            except: st.write("🤖")
        with c_title:
            st.subheader("NexBot AI")
            st.caption("Your Hiring Assistant")

        # 1. Initialize Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 2. Chat History Display (Scrollable)
        chat_container = st.container(height=350) # Increased height slightly
        with chat_container:
            if not st.session_state.messages:
                st.markdown("👋 **Hi! I'm NexBot.**")
                st.caption("Ask me about candidates, interview questions, or how to use this app.")
            
            for message in st.session_state.messages:
                # Use a different avatar for user vs assistant
                avatar = "chat.png" if message["role"] == "assistant" else None
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        # 3. Chat Input
        if prompt := st.chat_input("Ask NexBot...", key="sidebar_chat_input"):
            # A. Display User Message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # B. Get AI Response
            with st.spinner("Thinking..."):
                # Call the AI function
                response = ai.get_chat_response(st.session_state.messages)
            
            # C. Display AI Response
            st.session_state.messages.append({"role": "assistant", "content": response})
            with chat_container:
                with st.chat_message("assistant", avatar="chat.png"): # Use icon for response too
                    st.markdown(response)
        # --- CHATBOT SECTION END ---

        st.divider()
        st.subheader("Connect with Developer")
        st.link_button("LinkedIn Profile", "https://www.linkedin.com/in/karunyakp")
        st.link_button("GitHub Profile", "https://github.com/karunyakp")
        st.divider()
        st.caption("Developed & Maintained by")
        st.markdown("### Karunya. K. P") 
        st.caption("© 2025 NexHire Systems")

def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write(""); st.write("")
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                try: st.image("logo.png", use_container_width=True)
                except: st.markdown("<h1 style='text-align: center; color: #4F46E5;'>NexHire</h1>", unsafe_allow_html=True)
            st.write("")
            tab_sign, tab_reg = st.tabs(["Sign In", "Register New Account"])
            with tab_sign:
                st.write("")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Access Dashboard"):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        if ai.validate_admin_login(username, password): 
                            db.set_admin(username)
                        st.rerun()
                    else: st.error("Invalid credentials.")
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.info("Password must be at least 8 characters.")
                st.write("")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        if len(new_pass) < 8: st.error("Password is too short!")
                        else:
                            if db.add_user(new_user, new_pass):
                                if ai.validate_admin_login(new_user, new_pass):
                                    db.set_admin(new_user)
                                    st.success("Admin Credentials Verified! Please Login.")
                                else: st.success("Account created! Please log in.")
                            else: st.error("Username taken.")
                    else: st.warning("Please fill all fields.")
            st.write(""); st.divider()
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.caption("Application Developed by")
            st.markdown("**Karunya. K. P**") 
            st.caption("© 2025 NexHire Systems")
            st.markdown("</div>", unsafe_allow_html=True)

def dashboard_page():
    c_left, c_right = st.columns([6, 1])
    with c_left:
        cl1, cl2 = st.columns([1, 10])
        with cl1:
            try: st.image("logo.png", width=100)
            except: st.write("")
        with cl2:
            st.markdown(f"### Hello, {st.session_state['username']}")
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Your recruitment analytics overview</p>", unsafe_allow_html=True)
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            # Clear session state on logout
            keys_to_remove = ['analysis_result', 'analysis_complete']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    st.divider()

    if db.is_admin(st.session_state['username']):
        st.markdown("### Super Admin Console")
        st.info("Full Access to User Data, Resumes, and AI Outputs.")
        with st.expander("View Full Database (Click to Expand)", expanded=True):
            all_data = db.get_all_full_analysis()
            if all_data:
                df = pd.DataFrame(all_data, columns=['ID', 'User', 'Role', 'Resume', 'JD', 'Score', 'Feedback', 'Cover Letter', 'Interview', 'Market', 'Roadmap', 'Date'])
                st.dataframe(df[['ID', 'Date', 'User', 'Role', 'Score']], use_container_width=True)
                st.divider()
                st.markdown("### Deep Inspection")
                selected_id = st.selectbox("Select an ID to inspect full details:", df['ID'])
                if selected_id:
                    record = df[df['ID'] == selected_id].iloc[0]
                    st.success(f"Inspecting Record #{selected_id} | User: {record['User']}")
                    with st.expander("Resume & Job Description (Inputs)"):
                        c1, c2 = st.columns(2)
                        with c1: 
                            st.caption("Resume Text")
                            st.text_area("Resume", record['Resume'], height=200, key="adm_res")
                        with c2: 
                            st.caption("Job Description")
                            st.text_area("JD", record['JD'], height=200, key="adm_jd")
                    with st.expander("AI Feedback & Analysis (Outputs)"):
                        st.metric(label="Match Score", value=f"{record['Score']}%")
                        st.markdown("---")
                        st.markdown(record['Feedback'])
                    with st.expander("Generated Content (Drafts)"):
                        t1, t2, t3, t4 = st.tabs(["Cover Letter", "Interview Qs", "Market Data", "Roadmap"])
                        with t1: st.text_area("Cover Letter", record['Cover Letter'], key="adm_cl")
                        with t2: st.markdown(record['Interview'])
                        with t3: st.markdown(record['Market'])
                        with t4: st.markdown(record['Roadmap'])
            else:
                st.warning("No analysis data recorded yet.")
        st.divider()

    history = db.fetch_history(st.session_state['username'])
    last_score = history[0][3] if history else 0
    m1, m2 = st.columns(2)
    with m1:
        with st.container(border=True):
            st.metric(label="LATEST SCORE", value=f"{last_score}%", delta="Most Recent Scan")
    with m2:
        with st.container(border=True):
            st.metric(label="TOTAL SCANS", value=len(history), delta="Lifetime Usage")
    st.write("")
    
    col_main, col_side = st.columns([2, 1])
    with col_main:
        with st.container(border=True):
            st.markdown("### 1. Document Processing")
            uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed", key="resume_uploader")
            resume_text = ""
            category = "Manual Entry"
            
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages: resume_text += page.extract_text()
                
                with st.spinner("Categorizing profile..."):
                    category = ai.categorize_resume(resume_text)
                    st.success("Resume Extracted & Categorized!")
                    st.markdown(f"<span class='category-badge'>{category}</span>", unsafe_allow_html=True)
            else: 
                resume_text = st.text_area("Or paste raw text", height=200, placeholder="Paste resume content here...")

            if resume_text:
                st.write("")
                if st.button("Run AI & ATS Scanner", help="Check if resume looks AI-generated and is ATS friendly"):
                    with st.spinner("Scanning for AI patterns and ATS readability..."):
                        auth_data = ai.check_resume_authenticity(resume_text)
                        st.write("---")
                        st.markdown("### Authenticity Report")
                        s1, s2 = st.columns(2)
                        with s1:
                            h_score = auth_data.get('human_score', 0)
                            color = "normal" if h_score > 70 else "inverse"
                            st.metric("Human-Written Score", f"{h_score}%", help="Lower score means high likelihood of AI generation.")
                        with s2:
                            st.caption("ATS Verdict")
                            st.info(auth_data.get('verdict', 'N/A'))
                        st.warning(auth_data.get('analysis', ''))

    with col_side:
        with st.container(border=True):
            st.markdown("### 2. Job Requisition")
            job_role = st.text_input("Role Title", placeholder="e.g. Product Designer")
            job_desc = st.text_area("Requirements", height=250, placeholder="Paste Job Description here...", label_visibility="collapsed")
    st.write("")
    
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        run_quick_scan = st.button("Calculate Match Score", use_container_width=True, help="Instantly calculate ATS Score and Missing Keywords")
    with btn_col2:
        run_full_scan = st.button("Initialize Intelligence Engine", type="primary", use_container_width=True, help="Full deep dive with AI generation")

    # --- QUICK SCAN LOGIC ---
    if run_quick_scan:
        if resume_text and job_desc:
            with st.spinner("Calculating ATS Match Score..."):
                score, missing_keywords = ai.get_ats_score(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                st.divider()
                st.markdown("### ATS Score Analysis")
                q1, q2 = st.columns([1, 2])
                with q1:
                    st.metric(label="ATS Match Score", value=f"{score}%", delta="Instant Result")
                with q2:
                    if missing_keywords:
                        st.error(f"**Missing Critical Keywords:**\n{', '.join(missing_keywords)}")
                    else:
                        st.success("Excellent Match! No critical keywords missing.")
        else:
             st.warning("Please provide both a Resume and a Job Description.")

    # --- FULL SCAN LOGIC (PERSISTENT STATE) ---
    if run_full_scan:
        if resume_text and job_desc:
            with st.status("Launching NexHire Intelligence Engine...", expanded=True) as status:
                st.warning("Please wait! This deep analysis may take 1-2 minutes. Do not refresh the page.")
                st.write("Analyzing Resume & Job Description...")
                
                score, missing_keywords = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                
                resume_skills = af.extract_skills(resume_text)
                job_skills = af.extract_skills(job_desc)
                
                st.write("Drafting Cover Letter & Interview Questions...")
                cover_letter = ai.generate_cover_letter(resume_text, job_desc)
                interview_q = ai.generate_interview_questions(resume_text, job_desc)
                
                st.write("Calculating Market Value & Learning Roadmap...")
                market_analysis = ai.get_market_analysis(resume_text, job_role)
                roadmap = ai.generate_learning_roadmap(resume_text, job_desc)
                
                db.save_scan(st.session_state['username'], job_role, score)
                db.save_full_analysis(st.session_state['username'], job_role, resume_text, job_desc, score, feedback, cover_letter, interview_q, market_analysis, roadmap)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
                
                # STORE RESULTS IN SESSION STATE
                st.session_state['analysis_complete'] = True
                st.session_state['analysis_result'] = {
                    'score': score,
                    'feedback': feedback,
                    'resume_skills': resume_skills,
                    'job_skills': job_skills,
                    'missing_keywords': missing_keywords,
                    'cover_letter': cover_letter,
                    'interview_q': interview_q,
                    'market_analysis': market_analysis,
                    'roadmap': roadmap,
                    'category': category
                }
        else:
            st.warning("Please provide both a Resume and a Job Description.")

    # --- DISPLAY RESULTS FROM SESSION STATE ---
    if st.session_state.get('analysis_complete', False) and 'analysis_result' in st.session_state:
        res = st.session_state['analysis_result']
        
        st.divider()
        tab1, tab2, tab3, tab4 = st.tabs(["Analysis Report", "Cover Letter", "Interview Prep", "Strategic Insights"])
        
        with tab1:
            r1, r2 = st.columns([1, 2])
            with r1:
                with st.container(border=True):
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.markdown("### MATCH SCORE")
                    st.metric(label="", value=f"{res['score']}%", help="Strict ATS Calculation")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.write("")
                    
                    # --- UPDATED PDF GENERATION CALL ---
                    pdf_data = af.generate_pdf_report(
                        st.session_state['username'], 
                        job_role, 
                        res['score'], 
                        res['feedback'], 
                        res['resume_skills'], 
                        res['missing_keywords'], 
                        res['category'],
                        res['interview_q'],        # PASSED NEW DATA
                        res['market_analysis'],    # PASSED NEW DATA
                        res['roadmap']             # PASSED NEW DATA
                    )
                    # -----------------------------------

                    st.download_button("Download Report", data=pdf_data, file_name=f"NexHire_Report.pdf", mime="application/pdf")
            with r2:
                with st.container(border=True):
                    st.markdown("### SKILL GAP ANALYSIS")
                    matched = [s for s in res['resume_skills'] if s in res['job_skills']]
                    
                    if matched:
                        st.markdown("**Matched Skills**")
                        st.markdown("".join([f"<span class='skill-tag skill-match'>{s}</span>" for s in matched]), unsafe_allow_html=True)
                    st.write("")
                    if res['missing_keywords']:
                        st.markdown("**Missing Skills (AI Detected)**")
                        st.markdown("".join([f"<span class='skill-tag skill-missing'>{s}</span>" for s in res['missing_keywords'][:10]]), unsafe_allow_html=True)
                    st.divider()
                    st.write(res['feedback'])
        with tab2:
            with st.container(border=True):
                st.markdown("### AI-Generated Cover Letter")
                st.text_area("Copy this draft:", value=res['cover_letter'], height=400)
        with tab3:
            with st.container(border=True):
                st.markdown("### Interview Questions")
                st.markdown(res['interview_q'])
        with tab4:
            d1, d2 = st.columns([1.5, 1])
            with d1:
                with st.container(border=True):
                    st.markdown("### Market Value & Salary")
                    st.info("Based on 2025 Market Trends.")
                    st.markdown(res['market_analysis'])
                st.write("")
                with st.container(border=True):
                    st.markdown("### Candidate Upskilling Roadmap")
                    st.success("Suggested 4-Week Plan to bridge skill gaps:")
                    st.markdown(res['roadmap'])
            with d2:
                with st.container(border=True):
                    st.markdown("### Recruiter Outreach")
                    email_type = st.selectbox("Select Email Type", ["Interview Invite", "Polite Rejection", "Offer Letter"])
                    if st.button("Generate Email Draft"):
                        with st.spinner("Drafting..."):
                            email_draft = ai.generate_email_draft(resume_text, job_role, email_type)
                            st.text_area("Email Draft:", value=email_draft, height=250)

def main():
    setup_page()
    db.create_tables()
    render_sidebar()
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    if 'username' not in st.session_state: st.session_state['username'] = ""
    if not st.session_state['logged_in']: login_page()
    else: dashboard_page()

if __name__ == "__main__":
    main()
