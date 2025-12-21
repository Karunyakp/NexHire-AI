import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="NexHire", page_icon="💜", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #111827; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: white; border-radius: 12px; border: 1px solid #E5E7EB; padding: 25px; }
    .skill-badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-right: 5px; display: inline-block; }
    .match { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    .partial { background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }
    .missing { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def extract_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([page.extract_text() for page in reader.pages])
    except: return None

# --- SIDEBAR WITH ADMIN LOGIN ---
def render_sidebar():
    with st.sidebar:
        try: st.image("logo.png", width=150) 
        except: pass 
        st.title("NexHire")
        st.markdown("### Recruitment Intelligence")
        st.divider()
        
        # Admin Access in Sidebar
        with st.expander("🔐 Admin Access"):
            user = st.text_input("Username", key="adm_user")
            pwd = st.text_input("Password", type="password", key="adm_pwd")
            if st.button("Login"):
                if ai.validate_admin_login(user, pwd):
                    st.session_state['admin_logged_in'] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
        
        if st.session_state.get('admin_logged_in'):
            if st.button("Logout"):
                st.session_state['admin_logged_in'] = False
                st.rerun()

        st.divider()
        st.subheader("Developer")
        st.link_button("🔗 LinkedIn", "https://www.linkedin.com/in/karunyakp")
        st.link_button("💻 GitHub", "https://github.com/karunyakp")
        
        st.markdown("---")
        st.caption("Developed & Maintained by")
        st.markdown("**Karunya. K. P**") 
        st.caption("© 2025 NexHire Systems")

# --- 🎓 CANDIDATE MODE ---
def candidate_mode():
    st.markdown("## 🎓 Candidate Preparation")
    st.caption("Analyze your job fit and generate improvement plans.")
    
    # 1. INPUT
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Resume", type="pdf", key="c_res")
    with c2: jd = st.text_area("Paste Job Description", height=100, key="c_jd")
    
    if st.button("Analyze Job Fit", type="primary", use_container_width=True):
        if resume and jd:
            with st.spinner("Analyzing profile..."):
                text = extract_text(resume)
                st.session_state['c_data'] = ai.analyze_fit(text, jd)
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                st.session_state['show_interview'] = False
                st.session_state['show_roadmap'] = False
                st.session_state['show_sim'] = False
                st.session_state['show_compare'] = False
                db.save_scan("Candidate", "Job Fit Analysis", st.session_state['c_data'].get('score', 0))

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
        if b4.button("⚖️ Compare Version"): st.session_state['show_compare'] = True
            
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
                    comp_data = ai.compare_versions(st.session_state['c_text'], text_v2, st.session_state['c_jd'])
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
    
    # BIAS FREE TOGGLE
    bias_free = st.toggle("Enable Bias-Free Evaluation (Hide Name/Gender/Location)")
    
    if st.button("Run Screening", type="primary", use_container_width=True):
        if resume and jd:
            with st.spinner("Screening..."):
                text = extract_text(resume)
                st.session_state['r_data'] = ai.run_screening(text, jd, bias_free)
                st.session_state['r_text'] = text
                st.session_state['r_jd'] = jd
                db.save_scan("Recruiter", "Screening", st.session_state['r_data'].get('ats_score', 0))

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
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("No data found.")

# --- MAIN ---
def main():
    db.create_tables()
    render_sidebar()
    
    # Check if Admin Logged In
    if st.session_state.get('admin_logged_in'):
        admin_console()
    else:
        # Public View
        c1, c2 = st.columns([1, 5])
        with c1: st.image("logo.png", width=100)
        with c2: 
            st.title("NexHire")
            st.caption("Role Readiness & Recruitment Intelligence")
        
        tab1, tab2 = st.tabs(["🎓 Candidate Mode", "🧑‍💼 Recruiter Mode"])
        with tab1: candidate_mode()
        with tab2: recruiter_mode()
        
        st.divider()
        st.caption("🔒 Privacy Note: Documents are processed in-memory and not stored. Decisions should be made by humans, not AI.")

if __name__ == "__main__":
    main()
