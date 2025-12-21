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
                # Save to session state to prevent reload loss
                st.session_state['c_data'] = ai.analyze_fit(text, jd)
                st.session_state['c_text'] = text
                st.session_state['c_jd'] = jd
                # Reset extra states
                st.session_state['show_interview'] = False
                st.session_state['show_roadmap'] = False
                st.session_state['show_sim'] = False
                # Silent Save
                db.save_scan("Candidate", "Job Fit Analysis", st.session_state['c_data'].get('score', 0))

    # 2. OUTPUT (Fixed Order)
    if 'c_data' in st.session_state and st.session_state['c_data']:
        data = st.session_state['c_data']
        
        st.divider()
        # A. SCORE
        c_score, c_text = st.columns([1, 3])
        with c_score: st.metric("Readiness Score", f"{data['score']}%")
        with c_text: st.info(f"💡 {data['summary']}")
        
        # B. SKILLS
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
        
        # C. INSIGHTS (Always Visible)
        st.subheader("🔍 Experience Alignment")
        with st.spinner("Loading insights..."):
            st.write(ai.get_insights(st.session_state['c_text'], st.session_state['c_jd']))
            
        st.subheader("💡 Improvement Suggestions")
        with st.spinner("Loading suggestions..."):
            st.write(ai.get_improvements(st.session_state['c_text'], st.session_state['c_jd']))
            
        st.divider()
        
        # D. EXTRA FEATURES (Buttons)
        st.markdown("### 🛠️ Preparation Tools")
        b1, b2, b3 = st.columns(3)
        
        if b1.button("🎤 Generate Interview Prep"):
            st.session_state['show_interview'] = True
        if b2.button("📅 Generate 30-Day Plan"):
            st.session_state['show_roadmap'] = True
        if b3.button("🔮 What-If Skill Simulator"):
            st.session_state['show_sim'] = True
            
        # Display Extras
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

# --- 🧑‍💼 RECRUITER MODE ---
def recruiter_mode():
    st.markdown("## 🧑‍💼 Recruiter Screening")
    st.caption("AI-Assisted screening for efficiency.")
    
    c1, c2 = st.columns([1, 1])
    with c1: resume = st.file_uploader("Upload Resume", type="pdf", key="r_res")
    with c2: jd = st.text_area("Paste Job Description", height=100, key="r_jd")
    
    if st.button("Run Screening", type="primary", use_container_width=True):
        if resume and jd:
            with st.spinner("Screening..."):
                text = extract_text(resume)
                st.session_state['r_data'] = ai.run_screening(text, jd)
                st.session_state['r_text'] = text
                st.session_state['r_jd'] = jd
                st.session_state['show_explain'] = False
                # Silent Save
                db.save_scan("Recruiter", "Screening", st.session_state['r_data'].get('ats_score', 0))

    if 'r_data' in st.session_state and st.session_state['r_data']:
        data = st.session_state['r_data']
        st.divider()
        
        # 1. METRICS
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
            
        # 2. SUMMARY
        st.subheader("Candidate Summary")
        st.write(data['summary'])
        
        # 3. EXTRA
        if st.button("🤔 Why this score?"):
            with st.spinner("Analyzing logic..."):
                st.write(ai.explain_score(st.session_state['r_text'], st.session_state['r_jd'], data['ats_score']))

# --- HIDDEN ADMIN ---
def hidden_admin():
    try:
        if st.query_params.get("mode") != st.secrets["admin"]["hidden_route"]: return
    except: return

    st.markdown("## 🛡️ Admin Console")
    pwd = st.text_input("Password", type="password")
    if pwd == st.secrets["admin"]["password"]:
        st.success("Access Granted")
        st.dataframe(db.get_all_full_analysis())

# --- MAIN ---
def main():
    db.create_tables()
    hidden_admin() # Checks URL first
    
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
