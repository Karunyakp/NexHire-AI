import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
import advanced_features as af
import PyPDF2
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="NexHire", page_icon="💼", layout="wide")

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
    
    /* Badges */
    .category-badge {
        background-color: #EEF2FF;
        color: #4F46E5;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 12px;
        letter-spacing: 0.025em;
        border: 1px solid #C7D2FE;
    }

    /* Hide Footer only, keep header for settings */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def extract_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in reader.pages])
    except: return None

# --- 3. LOGIN PAGE ---
def login_page():
    # Centered Layout
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.write("")
        st.write("")
        with st.container(border=True):
            # Header
            st.markdown("""
                <div style="text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 40px; margin-bottom: 10px;">💼</div>
                    <h2 style="margin: 0; font-weight: 700; color: #111827; font-size: 24px;">NexHire</h2>
                    <p style="margin: 8px 0 0 0; color: #6B7280; font-size: 14px;">Enterprise Recruitment Intelligence</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Auth Tabs - ADDED ADMIN TAB HERE
            tab_login, tab_reg, tab_admin = st.tabs(["Sign In", "Create Account", "Admin"])
            
            with tab_login:
                u = st.text_input("Username", key="l_user")
                p = st.text_input("Password", type="password", key="l_pwd")
                if st.button("Sign In", type="primary", use_container_width=True):
                    if db.login_user(u, p):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = u
                        st.session_state['role'] = 'User' # Default user role
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
            
            with tab_admin:
                st.markdown("**Administrator Access**")
                admin_u = st.text_input("Admin Username", key="a_user")
                admin_p = st.text_input("Admin Password", type="password", key="a_pwd")
                if st.button("Access Admin Console", type="primary", use_container_width=True):
                    if ai.validate_admin_login(admin_u, admin_p):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = admin_u
                        st.session_state['role'] = 'Admin'
                        st.session_state['is_guest'] = False
                        st.session_state['admin_unlocked'] = True
                        st.rerun()
                    else:
                        st.error("Access Denied.")

            st.markdown("""
                <div style="text-align: center; margin: 20px 0;">
                    <span style="background-color: white; padding: 0 10px; color: #9CA3AF; font-size: 12px;">OR CONTINUE AS</span>
                </div>
            """, unsafe_allow_html=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                if st.button("Guest Candidate", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = "Guest Candidate"
                    st.session_state['role'] = "Candidate" # Explicit Role
                    st.session_state['is_guest'] = True
                    st.session_state['admin_unlocked'] = False
                    st.rerun()
            with col_g2:
                if st.button("Guest Recruiter", use_container_width=True):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = "Guest Recruiter"
                    st.session_state['role'] = "Recruiter" # Explicit Role
                    st.session_state['is_guest'] = True
                    st.session_state['admin_unlocked'] = False
                    st.rerun()

# --- 4. SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        try: st.image("logo.png", width=120) 
        except: pass 
        
        st.markdown(f"### {st.session_state.get('username', 'Guest')}")
        st.caption(f"Role: {st.session_state.get('role', 'Viewer')}")
        
        st.write("")
        if st.button("Sign Out", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        st.markdown("### Resources")
        st.markdown("[Documentation](#)")
        st.markdown("[Support](#)")
        
        st.markdown("---")
        # ADDED DEVELOPER CREDIT HERE
        st.markdown("**Developed by**")
        st.markdown("Karunya K. P.")
        st.caption("© 2025 NexHire Inc.")

# --- 5. CANDIDATE MODE ---
def candidate_mode():
    st.markdown("### 🎓 Candidate Dashboard")
    st.caption("Optimize your profile to get hired faster.")
    
    # DISTINCT LAYOUT
    c1, c2 = st.columns([1, 1])
    with c1: 
        resume = st.file_uploader("Upload Your Resume (PDF)", type="pdf", key="c_res")
    with c2: 
        jd = st.text_area("Paste Job Description", height=150, key="c_jd", placeholder="Paste the job description you are applying for...")
    
    if resume and jd:
        st.write("")
        st.markdown("#### Actions")
        
        # DISTINCT BUTTONS FOR CANDIDATE ACTIONS
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            analyze_fit_btn = st.button("🚀 Analyze Job Fit", type="primary", use_container_width=True)
            
        with col_act2:
            skill_gap_btn = st.button("🔍 Skill Gap Analysis", use_container_width=True)
            
        with col_act3:
            ats_score_btn = st.button("📊 Check ATS Score", use_container_width=True)

        # Logic for "Analyze Job Fit" (General Analysis)
        if analyze_fit_btn:
             with st.spinner("Analyzing profile fit..."):
                text = extract_text(resume)
                st.session_state['c_data'] = ai.analyze_fit(text, jd)
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                # Reset specific views
                st.session_state['view_mode'] = 'fit'
                
                db.save_scan(
                    st.session_state['username'], "Candidate", "Job Fit Analysis", 
                    st.session_state['c_data'].get('score', 0), st.session_state['c_data']
                )

        # Logic for "Skill Gap"
        if skill_gap_btn:
             with st.spinner("Extracting skills..."):
                text = extract_text(resume)
                # Reuse analyze_fit for skills but set view mode
                st.session_state['c_data'] = ai.analyze_fit(text, jd) 
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                st.session_state['view_mode'] = 'skills'

        # Logic for "ATS Score"
        if ats_score_btn:
             with st.spinner("Calculating ATS score..."):
                text = extract_text(resume)
                # Use recruiter screening logic but display differently for candidate
                st.session_state['c_ats_data'] = ai.run_screening(text, jd) 
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                st.session_state['view_mode'] = 'ats'


    # DISPLAY RESULTS BASED ON VIEW MODE
    if 'view_mode' in st.session_state:
        st.divider()
        
        # VIEW: JOB FIT
        if st.session_state['view_mode'] == 'fit' and 'c_data' in st.session_state:
            data = st.session_state['c_data']
            c_score, c_text = st.columns([1, 3])
            with c_score: st.metric("Overall Match", f"{data['score']}%")
            with c_text: 
                st.info(f"**Summary:** {data['summary']}")
            
            with st.expander("Show Improvement Plan", expanded=True):
                st.write(ai.get_improvements(st.session_state['c_text'], st.session_state['c_jd']))

        # VIEW: SKILLS
        elif st.session_state['view_mode'] == 'skills' and 'c_data' in st.session_state:
            data = st.session_state['c_data']
            st.subheader("Skill Gap Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("✅ **You Have**")
                for s in data['skills']['matched']: st.success(s)
            with col2:
                st.markdown("⚠️ **Partial Match**")
                for s in data['skills']['partial']: st.warning(s)
            with col3:
                st.markdown("❌ **Missing**")
                for s in data['skills']['missing']: st.error(s)
                
            st.info("💡 **Tip:** Add the missing skills to your resume if you have experience with them!")

        # VIEW: ATS SCORE
        elif st.session_state['view_mode'] == 'ats' and 'c_ats_data' in st.session_state:
            data = st.session_state['c_ats_data']
            st.subheader("ATS Compatibility Check")
            
            m1, m2 = st.columns(2)
            with m1: st.metric("ATS Parse Score", f"{data['ats_score']}%")
            with m2: 
                if data['ats_score'] > 80: st.success("Your resume is highly readable by ATS.")
                elif data['ats_score'] > 50: st.warning("Your resume needs formatting improvements.")
                else: st.error("Your resume may be rejected by automated systems.")
            
            st.write("### How an ATS sees your resume:")
            st.write(data['summary'])

# --- 6. RECRUITER MODE ---
def recruiter_mode():
    st.markdown("### 🧑‍💼 Recruiter Workspace")
    st.caption("Screen candidates and detect red flags efficiently.")
    
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Candidate Resume", type="pdf", key="r_res")
    with c2: jd = st.text_area("Job Requirements", height=150, key="r_jd")
    
    bias_free = st.toggle("Enable Bias-Free Screening (Hide Name/Gender)")
    
    if st.button("Run Candidate Screening", type="primary"):
        if resume and jd:
            with st.spinner("Screening candidate..."):
                text = extract_text(resume)
                if text:
                    st.session_state['r_data'] = ai.run_screening(text, jd, bias_free)
                    st.session_state['r_text'] = text
                    st.session_state['r_jd'] = jd
                    # SAVE FULL DATA HERE
                    db.save_scan(
                        st.session_state['username'], 
                        "Recruiter", 
                        "Screening", 
                        st.session_state['r_data'].get('ats_score', 0),
                        st.session_state['r_data'] 
                    )
                else: st.error("Processing failed.")

    if 'r_data' in st.session_state and st.session_state['r_data']:
        data = st.session_state['r_data']
        st.divider()
        
        # DISTINCT RECRUITER METRICS
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("ATS Score", f"{data['ats_score']}%")
        with m2: 
            badge_color = "green" if "Human" in data['auth_badge'] else "red"
            st.markdown(f"**Authenticity:** :{badge_color}[{data['auth_badge']}]")
        with m3: 
            flags_count = len(data['red_flags'])
            st.metric("Red Flags Detected", flags_count, delta_color="inverse")
            
        st.subheader("⚠️ Risk Assessment")
        if data['red_flags']:
            for f in data['red_flags']: st.error(f"🚩 {f}")
        else: st.success("No critical red flags detected.")
            
        st.subheader("Candidate Summary")
        st.write(data['summary'])
        
        with st.expander("View Logic Explanation"):
            st.write(ai.explain_score(st.session_state['r_text'], st.session_state['r_jd'], data['ats_score']))

# --- 7. ADMIN CONSOLE ---
def admin_console():
    st.markdown("### System Administration")
    data = db.get_all_full_analysis()
    if data:
        # Added 'Details' to the column headers
        df = pd.DataFrame(data, columns=["Timestamp", "Username", "Mode", "Action", "Score", "Details"])
        st.dataframe(df, use_container_width=True)
    else: st.info("No system activity recorded.")

# --- 8. MAIN APP LOGIC ---
def main():
    db.create_tables()
    
    # Check for Login Status
    if not st.session_state.get('logged_in'):
        login_page()
    else:
        render_sidebar()
        
        # IF ADMIN
        if st.session_state.get('admin_unlocked'):
            admin_console()
            
        # IF USER or GUEST
        else:
            role = st.session_state.get('role', 'User')
            
            # Logic: 
            # If Candidate Role -> Show ONLY Candidate Tools
            # If Recruiter Role -> Show ONLY Recruiter Tools
            # If standard 'User' -> Show BOTH (e.g. standard registered user)
            
            if role == "Candidate":
                candidate_mode()
            elif role == "Recruiter":
                recruiter_mode()
            else:
                # Default User sees both via tabs
                tab1, tab2 = st.tabs(["Candidate Tools", "Recruiter Tools"])
                with tab1: candidate_mode()
                with tab2: recruiter_mode()

if __name__ == "__main__":
    main()
