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
    st.markdown("### Candidate Dashboard")
    st.caption("Optimize your profile for specific roles.")
    
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Resume (PDF)", type="pdf", key="c_res")
    with c2: jd = st.text_area("Job Description", height=200, key="c_jd", placeholder="Paste the job description here...")
    
    if resume:
        text = extract_text(resume)
        if text:
            if 'cat' not in st.session_state or st.session_state.get('last_res') != resume.name:
                with st.spinner("Analyzing document structure..."):
                    st.session_state['cat'] = ai.categorize_resume(text)
                    st.session_state['last_res'] = resume.name
            
            st.markdown(f"Profile Detected: <span class='category-badge'>{st.session_state['cat']}</span>", unsafe_allow_html=True)
            
            if st.button("Verify Authenticity", type="secondary"):
                with st.spinner("Verifying content origin..."):
                    auth_data = ai.check_authenticity(text)
                    if auth_data:
                        st.info(f"Authenticity Score: {auth_data.get('human_score', 0)}% - {auth_data.get('verdict')}")
                    else: st.error("Verification failed.")

    st.write("")
    if st.button("Analyze Fit", type="primary"):
        if resume and jd:
            with st.spinner("Processing analysis..."):
                text = extract_text(resume)
                st.session_state['c_data'] = ai.analyze_fit(text, jd)
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                
                for key in ['show_interview', 'show_roadmap', 'show_sim', 'show_compare']:
                    st.session_state[key] = False
                
                # SAVE FULL DATA HERE
                db.save_scan(
                    st.session_state['username'], 
                    "Candidate", 
                    "Analysis", 
                    st.session_state['c_data'].get('score', 0),
                    st.session_state['c_data'] # Passes the entire AI result
                )

    if 'c_data' in st.session_state and st.session_state['c_data']:
        data = st.session_state['c_data']
        
        st.divider()
        c_score, c_text = st.columns([1, 3])
        with c_score: 
            st.metric("Match Score", f"{data['score']}%")
        with c_text: 
            st.markdown("#### Summary")
            st.write(data['summary'])
        
        st.markdown("#### Skills Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Matched**")
            for s in data['skills']['matched']: st.caption(f"• {s}")
        with col2:
            st.markdown("**Partial Match**")
            for s in data['skills']['partial']: st.caption(f"• {s}")
        with col3:
            st.markdown("**Missing**")
            for s in data['skills']['missing']: st.caption(f"• {s}")
            
        st.divider()
        
        with st.expander("Detailed Insights"):
            st.write(ai.get_insights(st.session_state['c_text'], st.session_state['c_jd']))
            
        with st.expander("Recommendations"):
            st.write(ai.get_improvements(st.session_state['c_text'], st.session_state['c_jd']))
            
        st.write("")
        st.markdown("#### Tools")
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("Interview Questions"): st.session_state['show_interview'] = True
        if b2.button("Learning Roadmap"): st.session_state['show_roadmap'] = True
        if b3.button("Skill Simulator"): st.session_state['show_sim'] = True
        if b4.button("Compare Versions"): st.session_state['show_compare'] = True
            
        if st.session_state.get('show_interview'):
            st.markdown("##### Interview Preparation")
            st.write(ai.get_interview_prep(st.session_state['c_text'], st.session_state['c_jd']))
            
        if st.session_state.get('show_roadmap'):
            st.markdown("##### 30-Day Plan")
            st.write(ai.get_roadmap(st.session_state['c_text'], st.session_state['c_jd']))
            
        if st.session_state.get('show_sim'):
            st.markdown("##### Simulator")
            new_skill = st.text_input("Simulate adding a skill:")
            if new_skill:
                sim_res = ai.simulate_skill(st.session_state['c_text'], st.session_state['c_jd'], data['score'], new_skill)
                st.metric("Projected Score", f"{sim_res['new_score']}%", delta=f"{sim_res['new_score'] - data['score']}%")
                st.write(sim_res['comment'])
                
        if st.session_state.get('show_compare'):
            st.markdown("##### Version Comparison")
            res_v2 = st.file_uploader("Upload Secondary Resume", type="pdf", key="v2_res")
            if res_v2 and st.button("Compare"):
                text_v2 = extract_text(res_v2)
                st.session_state['comp_data'] = ai.compare_versions(st.session_state['c_text'], text_v2, st.session_state['c_jd'])
                
                if 'comp_data' in st.session_state:
                    comp_data = st.session_state['comp_data']
                    cc1, cc2 = st.columns(2)
                    with cc1: st.metric("Primary Score", f"{comp_data['v1_score']}%")
                    with cc2: st.metric("Secondary Score", f"{comp_data['v2_score']}%")
                    st.write(f"**Verdict:** {comp_data['improvement']}")

# --- 6. RECRUITER MODE ---
def recruiter_mode():
    st.markdown("### Recruiter Workspace")
    st.caption("Efficiently screen and evaluate candidates.")
    
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Candidate Resume", type="pdf", key="r_res")
    with c2: jd = st.text_area("Job Requirements", height=200, key="r_jd")
    
    bias_free = st.toggle("Enable Bias-Free Screening")
    
    if st.button("Screen Candidate", type="primary"):
        if resume and jd:
            with st.spinner("Screening..."):
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
                        st.session_state['r_data'] # Passes the entire AI result
                    )
                else: st.error("Processing failed.")

    if 'r_data' in st.session_state and st.session_state['r_data']:
        data = st.session_state['r_data']
        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("ATS Score", f"{data['ats_score']}%")
        with m2: st.markdown(f"**Authenticity:** {data['auth_badge']}")
        with m3: 
            st.markdown("**Flags:**")
            if data['red_flags']:
                for f in data['red_flags']: st.error(f)
            else: st.success("No flags detected")
            
        st.markdown("#### Evaluation Summary")
        st.write(data['summary'])
        
        if st.button("View Score Logic"):
            with st.spinner("Generating logic explanation..."):
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
