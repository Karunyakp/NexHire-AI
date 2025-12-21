import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
import advanced_features as af
import PyPDF2
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="NexHire Platinum", page_icon="💜", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #111827; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .login-container { text-align: center; margin-bottom: 20px; }
    div[data-testid="stMetricValue"] { font-size: 32px !important; color: #4F46E5; }
    
    .skill-badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-right: 5px; display: inline-block; }
    .match { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    .partial { background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }
    .missing { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
    .category-badge { background-color: #EEF2FF; color: #4F46E5; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 14px; border: 1px solid #C7D2FE; }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def extract_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in reader.pages])
    except: return None

# --- AUTHENTICATION ---
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("")
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1: st.image("logo.png", use_container_width=True)
            with c2: 
                st.markdown("## NexHire")
                st.caption("Enterprise Recruitment Intelligence")
            
            st.divider()
            tab_login, tab_reg = st.tabs(["🔐 Login", "📝 Register"])
            
            with tab_login:
                u = st.text_input("Username", key="l_user")
                p = st.text_input("Password", type="password", key="l_pwd")
                if st.button("Sign In", type="primary", use_container_width=True):
                    if db.login_user(u, p):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = u
                        st.session_state['is_guest'] = False
                        st.rerun()
                    else:
                        st.error("Invalid Credentials")
            
            with tab_reg:
                new_u = st.text_input("Choose Username", key="r_user")
                new_p = st.text_input("Choose Password", type="password", key="r_pwd")
                if st.button("Create Account", use_container_width=True):
                    if len(new_p) < 4: st.error("Password too short")
                    elif db.add_user(new_u, new_p): st.success("Account Created! Please Sign In.")
                    else: st.error("Username taken.")

            st.markdown("---")
            if st.button("🚀 Continue as Guest", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['username'] = "Guest"
                st.session_state['is_guest'] = True
                st.rerun()

# --- SIDEBAR ---
def render_sidebar():
    with st.sidebar:
        try: st.image("logo.png", width=150) 
        except: pass 
        
        st.write(f"Logged in as: **{st.session_state.get('username', 'Guest')}**")
        if not st.session_state.get('is_guest'):
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()
        
        st.divider()
        st.subheader("Connect")
        st.link_button("🔗 LinkedIn", "https://www.linkedin.com/in/karunyakp")
        st.link_button("💻 GitHub", "https://github.com/karunyakp")
        st.markdown("---")
        st.caption("Developed by **Karunya. K. P**") 
        st.caption("© 2025 NexHire Systems")

# --- 🎓 CANDIDATE MODE ---
def candidate_mode():
    st.markdown("## 🎓 Candidate Preparation")
    st.caption("Analyze your job fit, check authenticity, and get improvements.")
    
    # 1. INPUT
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Resume", type="pdf", key="c_res")
    with c2: jd = st.text_area("Paste Job Description", height=100, key="c_jd")
    
    # Process Resume Logic (Category + Authenticity)
    if resume:
        text = extract_text(resume)
        if text:
            # Categorization
            if 'cat' not in st.session_state or st.session_state.get('last_res') != resume.name:
                with st.spinner("Processing..."):
                    st.session_state['cat'] = ai.categorize_resume(text)
                    st.session_state['last_res'] = resume.name
            
            st.markdown(f"**Detected Profile:** <span class='category-badge'>{st.session_state['cat']}</span>", unsafe_allow_html=True)
            
            # Authenticity Check (RESTORED BUTTON)
            if st.button("🛡️ Check Authenticity & ATS Readability"):
                with st.spinner("Scanning for AI patterns..."):
                    auth_data = ai.check_authenticity(text)
                    if auth_data:
                        st.info("### Authenticity Report")
                        a1, a2 = st.columns(2)
                        with a1: 
                            score = auth_data.get('human_score', 0)
                            st.metric("Human-Written Score", f"{score}%")
                        with a2: 
                            st.write(f"**Verdict:** {auth_data.get('verdict')}")
                            st.caption(auth_data.get('analysis'))
                    else: st.error("Scan failed.")

    st.divider()
    
    # Main Analysis Button
    if st.button("Analyze Job Fit", type="primary", use_container_width=True):
        if resume and jd:
            with st.spinner("Analyzing profile..."):
                text = extract_text(resume)
                st.session_state['c_data'] = ai.analyze_fit(text, jd)
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                # Reset tool states
                for key in ['show_interview', 'show_roadmap', 'show_sim', 'show_compare']:
                    st.session_state[key] = False
                
                # Save scan
                db.save_scan(st.session_state['username'], "Candidate", "Job Fit Analysis", st.session_state['c_data'].get('score', 0))

    # 2. OUTPUT
    if 'c_data' in st.session_state and st.session_state['c_data']:
        data = st.session_state['c_data']
        
        st.divider()
        c_score, c_text = st.columns([1, 3])
        with c_score: st.metric("Readiness Score", f"{data['score']}%")
        with c_text: st.info(f"💡 {data['summary']}")
        
        st.subheader("Skill Match Breakdown")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**✅ Matched**")
            for s in data['skills']['matched']: st.markdown(f"<span class='skill-badge match'>{s}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown("**⚠ Partial**")
            for s in data['skills']['partial']: st.markdown(f"<span class='skill-badge partial'>{s}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown("**❌ Missing**")
            for s in data['skills']['missing']: st.markdown(f"<span class='skill-badge missing'>{s}</span>", unsafe_allow_html=True)
            
        st.divider()
        st.subheader("🔍 Experience Alignment")
        st.write(ai.get_insights(st.session_state['c_text'], st.session_state['c_jd']))
        st.subheader("💡 Improvement Suggestions")
        st.write(ai.get_improvements(st.session_state['c_text'], st.session_state['c_jd']))
            
        st.divider()
        st.markdown("### 🛠️ Preparation Tools")
        b1, b2, b3, b4 = st.columns(4)
        
        if b1.button("🎤 Interview Prep"): st.session_state['show_interview'] = True
        if b2.button("📅 30-Day Plan"): st.session_state['show_roadmap'] = True
        if b3.button("🔮 What-If Simulator"): st.session_state['show_sim'] = True
        if b4.button("⚖️ Compare Versions"): st.session_state['show_compare'] = True
            
        if st.session_state.get('show_interview'):
            st.success("### Interview Questions")
            st.write(ai.get_interview_prep(st.session_state['c_text'], st.session_state['c_jd']))
            
        if st.session_state.get('show_roadmap'):
            st.warning("### 30-Day Improvement Plan")
            st.write(ai.get_roadmap(st.session_state['c_text'], st.session_state['c_jd']))
            
        if st.session_state.get('show_sim'):
            st.info("### Skill Simulator")
            new_skill = st.text_input("Enter a skill to add (e.g., 'Docker'):")
            if new_skill:
                sim_res = ai.simulate_skill(st.session_state['c_text'], st.session_state['c_jd'], data['score'], new_skill)
                st.metric("Simulated New Score", f"{sim_res['new_score']}%", delta=f"{sim_res['new_score'] - data['score']}%")
                st.write(sim_res['comment'])
                
        if st.session_state.get('show_compare'):
            st.info("### Compare Resume Versions")
            res_v2 = st.file_uploader("Upload Modified Resume (V2)", type="pdf", key="v2_res")
            if res_v2:
                if st.button("Compare V1 vs V2"):
                    text_v2 = extract_text(res_v2)
                    if text_v2:
                        st.session_state['comp_data'] = ai.compare_versions(st.session_state['c_text'], text_v2, st.session_state['c_jd'])
                    else: st.error("Error reading V2 resume.")
                
                if 'comp_data' in st.session_state:
                    comp_data = st.session_state['comp_data']
                    cc1, cc2 = st.columns(2)
                    with cc1: st.metric("V1 Score", f"{comp_data['v1_score']}%")
                    with cc2: st.metric("V2 Score", f"{comp_data['v2_score']}%", delta=f"{comp_data['v2_score'] - comp_data['v1_score']}%")
                    st.write(f"**Verdict:** {comp_data['improvement']}")
                    st.write("**Key Changes:**")
                    for k in comp_data['key_changes']: st.write(f"- {k}")
                    st.write(f"**Advice:** {comp_data['advice']}")

# --- 🧑‍💼 RECRUITER MODE ---
def recruiter_mode():
    st.markdown("## 🧑‍💼 Recruiter Screening")
    st.caption("AI-Assisted screening for efficiency.")
    
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Resume", type="pdf", key="r_res")
    with c2: jd = st.text_area("Paste Job Description", height=100, key="r_jd")
    
    bias_free = st.toggle("Enable Bias-Free Evaluation (Hide Name/Gender/Location)")
    
    if st.button("Run Screening", type="primary", use_container_width=True):
        if resume and jd:
            with st.spinner("Screening..."):
                text = extract_text(resume)
                if text:
                    st.session_state['r_data'] = ai.run_screening(text, jd, bias_free)
                    st.session_state['r_text'] = text
                    st.session_state['r_jd'] = jd
                    db.save_scan(st.session_state['username'], "Recruiter", "Screening", st.session_state['r_data'].get('ats_score', 0))
                else: st.error("Could not read PDF.")

    if 'r_data' in st.session_state and st.session_state['r_data']:
        data = st.session_state['r_data']
        st.divider()
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("ATS Match Score", f"{data['ats_score']}%")
        with m2: 
            auth = data['auth_badge']
            color = "green" if auth == "Human" else "orange" if auth == "Mixed" else "red"
            st.markdown(f"**Authenticity:** :{color}[{auth}]")
        with m3: 
            st.markdown("**Red Flags:**")
            if data['red_flags']:
                for f in data['red_flags']: st.error(f)
            else: st.success("None Detected")
            
        st.subheader("Candidate Summary")
        st.write(data['summary'])
        
        if st.button("🤔 Why this score?"):
            with st.spinner("Analyzing logic..."):
                st.write(ai.explain_score(st.session_state['r_text'], st.session_state['r_jd'], data['ats_score']))

# --- ADMIN CONSOLE ---
def admin_console():
    st.markdown("## 🛡️ Admin Console")
    st.info("Authorized Access Only")
    data = db.get_all_full_analysis()
    if data:
        df = pd.DataFrame(data, columns=["Timestamp", "Username", "Mode", "Action", "Score"])
        st.dataframe(df, use_container_width=True)
    else: st.warning("No data found.")

# --- MAIN ---
def main():
    db.create_tables()
    
    # 🕵️ HIDDEN ADMIN ROUTE
    try: secret_mode = st.secrets["admin"]["hidden_route"]
    except: secret_mode = "secure_admin_view"
    
    if st.query_params.get("mode") == secret_mode:
        st.empty()
        st.header("🛡️ Secure Admin Login")
        u = st.text_input("Admin Username")
        p = st.text_input("Admin Password", type="password")
        if st.button("Authenticate"):
            if ai.validate_admin_login(u, p):
                st.session_state['admin_unlocked'] = True
                st.rerun()
            else: st.error("Access Denied.")
        if st.session_state.get('admin_unlocked'):
            admin_console()
            return

    # --- STANDARD APP ---
    if not st.session_state.get('logged_in'):
        login_page()
    else:
        render_sidebar()
        c1, c2 = st.columns([1, 5])
        with c1: st.image("logo.png", width=100)
        with c2: 
            st.title("NexHire")
            st.caption("Role Readiness & Recruitment Intelligence")
        
        # --- RESTORED DASHBOARD METRICS ---
        if not st.session_state.get('is_guest'):
            history = db.fetch_user_history(st.session_state['username'])
            if history:
                m1, m2 = st.columns(2)
                with m1: st.metric("Total Scans", len(history))
                with m2: st.metric("Latest Score", f"{history[0][4]}%")
                st.divider()

        tab1, tab2 = st.tabs(["🎓 Candidate Mode", "🧑‍💼 Recruiter Mode"])
        with tab1: candidate_mode()
        with tab2: recruiter_mode()
        
        st.divider()
        st.caption("🔒 Privacy Note: Documents are processed in-memory and not stored.")

if __name__ == "__main__":
    main()
