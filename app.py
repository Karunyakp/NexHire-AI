import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
import advanced_features as af
import PyPDF2
import time

# --- 1. CONFIGURATION & STYLING ---
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
        
        #MainMenu, footer, header {visibility: hidden;}
        div[data-testid="stHeaderActionElements"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        try: 
            # Increased Logo Size
            st.image("logo.png", width=150) 
        except: pass 
        st.title("NexHire")
        st.markdown("### Enterprise Recruitment Intelligence")
        st.divider()
        st.subheader("Connect with Developer")
        st.link_button("🔗 LinkedIn Profile", "https://www.linkedin.com/in/karunyakp")
        st.link_button("💻 GitHub Profile", "https://github.com/karunyakp")
        st.divider()
        st.caption("Developed & Maintained by")
        st.markdown("### Karunya. K. P") 
        st.caption("© 2025 NexHire Systems")

# --- 3. LOGIN PAGE ---
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
                        
                        # --- 🔒 SECURE ADMIN CHECK ---
                        if ai.validate_admin_login(username, password): 
                            db.set_admin(username)
                            
                        st.rerun()
                    else: st.error("Invalid credentials.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.info("ℹ️ Password must be at least 8 characters.")
                st.write("")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        if len(new_pass) < 8: st.error("❌ Password is too short!")
                        else:
                            if db.add_user(new_user, new_pass):
                                if ai.validate_admin_login(new_user, new_pass):
                                    db.set_admin(new_user)
                                    st.success("👑 Admin Credentials Verified! Please Login.")
                                else: st.success("Account created! Please log in.")
                            else: st.error("Username taken.")
                    else: st.warning("Please fill all fields.")
            st.write(""); st.divider()
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.caption("Application Developed by")
            st.markdown("**Karunya. K. P**") 
            st.caption("© 2025 NexHire Systems")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DASHBOARD PAGE ---
def dashboard_page():
    c_left, c_right = st.columns([6, 1])
    with c_left:
        cl1, cl2 = st.columns([1, 10])
        with cl1:
            try: 
                # Increased Logo Size
                st.image("logo.png", width=100)
            except: st.write("🔹")
        with cl2:
            st.markdown(f"### Hello, {st.session_state['username']}")
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Your recruitment analytics overview</p>", unsafe_allow_html=True)
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
    st.divider()

    # --- 🛡️ SUPER ADMIN CONSOLE ---
    if db.is_admin(st.session_state['username']):
        st.markdown("### 🛡️ Super Admin Console")
        st.info("Full Access to User Data, Resumes, and AI Outputs.")
        
        with st.expander("📂 View Full Database (Click to Expand)", expanded=True):
            all_data = db.get_all_full_analysis()
            if all_data:
                df = pd.DataFrame(all_data, columns=['ID', 'User', 'Role', 'Resume', 'JD', 'Score', 'Feedback', 'Cover Letter', 'Interview', 'Market', 'Roadmap', 'Date'])
                st.dataframe(df[['ID', 'Date', 'User', 'Role', 'Score']], use_container_width=True)
                
                st.divider()
                st.markdown("### 🔍 Deep Inspection")
                selected_id = st.selectbox("Select an ID to inspect full details:", df['ID'])
                if selected_id:
                    record = df[df['ID'] == selected_id].iloc[0]
                    st.success(f"Inspecting Record #{selected_id} | User: {record['User']}")
                    
                    with st.expander("📄 Resume & Job Description (Inputs)"):
                        c1, c2 = st.columns(2)
                        with c1: 
                            st.caption("Resume Text")
                            st.text_area("Resume", record['Resume'], height=200, key="adm_res")
                        with c2: 
                            st.caption("Job Description")
                            st.text_area("JD", record['JD'], height=200, key="adm_jd")
                    
                    with st.expander("🤖 AI Feedback & Analysis (Outputs)"):
                        # Using st.metric here too for clarity
                        st.metric(label="Match Score", value=f"{record['Score']}%")
                        st.markdown("---")
                        st.markdown(record['Feedback'])
                        
                    with st.expander("📝 Generated Content (Drafts)"):
                        t1, t2, t3, t4 = st.tabs(["Cover Letter", "Interview Qs", "Market Data", "Roadmap"])
                        with t1: st.text_area("Cover Letter", record['Cover Letter'], key="adm_cl")
                        with t2: st.markdown(record['Interview'])
                        with t3: st.markdown(record['Market'])
                        with t4: st.markdown(record['Roadmap'])
            else:
                st.warning("No analysis data recorded yet.")
        st.divider()

    # --- METRICS SECTION ---
    history = db.fetch_history(st.session_state['username'])
    # FIX: Column index 3 is score, index 2 was Role.
    last_score = history[0][3] if history else 0
    
    m1, m2 = st.columns(2)
    with m1:
        with st.container(border=True):
            # Replaced custom HTML with native metric for reliability
            st.metric(label="LATEST SCORE", value=f"{last_score}%", delta="Most Recent Scan")
    with m2:
        with st.container(border=True):
            st.metric(label="TOTAL SCANS", value=len(history), delta="Lifetime Usage")
    st.write("")
    
    # Input Area
    col_main, col_side = st.columns([2, 1])
    with col_main:
        with st.container(border=True):
            st.markdown("### 1. Document Processing")
            uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed", key="resume_uploader")
            resume_text = ""
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages: resume_text += page.extract_text()
                st.success("Resume Extracted")
            else: resume_text = st.text_area("Or paste raw text", height=200, placeholder="Paste resume content here...")

    with col_side:
        with st.container(border=True):
            st.markdown("### 2. Job Requisition")
            job_role = st.text_input("Role Title", placeholder="e.g. Product Designer")
            job_desc = st.text_area("Requirements", height=250, placeholder="Paste Job Description here...", label_visibility="collapsed")
    st.write("")
    
    # AI Engine Trigger
    if st.button("Initialize Intelligence Engine", type="primary"):
        if resume_text and job_desc:
            
            with st.status("🚀 Launching NexHire Intelligence Engine...", expanded=True) as status:
                st.warning("⏳ Please wait! This deep analysis may take 1-2 minutes. Do not refresh the page.")
                
                st.write("🔍 Analyzing Resume & Job Description...")
                # Core AI
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                resume_skills = af.extract_skills(resume_text)
                job_skills = af.extract_skills(job_desc)
                
                st.write("📝 Drafting Cover Letter & Interview Questions...")
                # Generative
                cover_letter = ai.generate_cover_letter(resume_text, job_desc)
                interview_q = ai.generate_interview_questions(resume_text, job_desc)
                
                st.write("💎 Calculating Market Value & Learning Roadmap...")
                # Strategic
                market_analysis = ai.get_market_analysis(resume_text, job_role)
                roadmap = ai.generate_learning_roadmap(resume_text, job_desc)
                
                # Save Data
                db.save_scan(st.session_state['username'], job_role, score)
                db.save_full_analysis(st.session_state['username'], job_role, resume_text, job_desc, score, feedback, cover_letter, interview_q, market_analysis, roadmap)
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
            
            st.divider()
            
            # --- RESULTS TABS ---
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis Report", "📝 Cover Letter", "🎤 Interview Prep", "🚀 Strategic Insights"])
            
            # TAB 1: REPORT
            with tab1:
                r1, r2 = st.columns([1, 2])
                with r1:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown("### MATCH SCORE")
                        # Using st.metric here guarantees visibility
                        st.metric(label="", value=f"{score}%", help="Strict ATS Calculation")
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.write("")
                        pdf_data = af.generate_pdf_report(st.session_state['username'], job_role, score, feedback, resume_skills, job_skills)
                        st.download_button("📄 Download Report", data=pdf_data, file_name=f"NexHire_Report.pdf", mime="application/pdf")
                with r2:
                    with st.container(border=True):
                        st.markdown("### 📊 SKILL GAP ANALYSIS")
                        matched = [s for s in resume_skills if s in job_skills]
                        missing = [s for s in job_skills if s not in resume_skills]
                        if matched:
                            st.markdown("**✅ Matched Skills**")
                            st.markdown("".join([f"<span class='skill-tag skill-match'>{s}</span>" for s in matched]), unsafe_allow_html=True)
                        st.write("")
                        if missing:
                            st.markdown("**❌ Missing Skills**")
                            st.markdown("".join([f"<span class='skill-tag skill-missing'>{s}</span>" for s in missing]), unsafe_allow_html=True)
                        st.divider()
                        st.write(feedback)
            
            # TAB 2: COVER LETTER
            with tab2:
                with st.container(border=True):
                    st.markdown("### 📝 AI-Generated Cover Letter")
                    st.text_area("Copy this draft:", value=cover_letter, height=400)
            
            # TAB 3: INTERVIEW
            with tab3:
                with st.container(border=True):
                    st.markdown("### 🎤 Interview Questions")
                    st.markdown(interview_q)

            # TAB 4: STRATEGIC INSIGHTS
            with tab4:
                d1, d2 = st.columns([1.5, 1])
                with d1:
                    with st.container(border=True):
                        st.markdown("### 💰 Market Value & Salary")
                        st.info("Based on 2025 Market Trends.")
                        st.markdown(market_analysis)
                    
                    st.write("")
                    with st.container(border=True):
                        st.markdown("### 📈 Candidate Upskilling Roadmap")
                        st.success("Suggested 4-Week Plan to bridge skill gaps:")
                        st.markdown(roadmap)
                        
                with d2:
                    with st.container(border=True):
                        st.markdown("### 📧 Recruiter Outreach")
                        email_type = st.selectbox("Select Email Type", ["Interview Invite", "Polite Rejection", "Offer Letter"])
                        if st.button("Generate Email Draft"):
                            with st.spinner("Drafting..."):
                                email_draft = ai.generate_email_draft(resume_text, job_role, email_type)
                                st.text_area("Email Draft:", value=email_draft, height=250)
        else:
            st.warning("⚠️ Please provide both a Resume and a Job Description.")

# --- 5. MAIN EXECUTION ---
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
