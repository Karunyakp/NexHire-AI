import streamlit as st
import database as db
import ai_engine as ai
import advanced_features as adv
import PyPDF2
import time
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="NexHire Pro", page_icon="📊", layout="wide")

# ============ THEME STYLING ============
def get_theme_css(theme="light"):
    dark = theme == "dark"
    bg_color = "#1E1E1E" if dark else "#F3F4F6"
    card_color = "#2D2D2D" if dark else "#FFFFFF"
    text_color = "#E0E0E0" if dark else "#1F2937"
    
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {text_color};
        background-color: {bg_color};
    }}

    .stApp {{
        background-color: {bg_color};
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] > div {{
        background-color: {card_color};
        border-radius: 12px;
        border: 1px solid {"#404040" if dark else "#E5E7EB"};
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, {"0.3" if dark else "0.08"});
        padding: 32px;
        transition: all 0.3s ease;
    }}

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color: {"#3A3A3A" if dark else "#F9FAFB"} !important;
        color: {text_color} !important;
    }}

    div.stButton > button {{
        background: linear-gradient(135deg, #6366F1 0%, #5B5FE8 100%);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        width: 100%;
        margin-top: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }}

    .metric-label {{
        color: {"#B0B0B0" if dark else "#6B7280"};
    }}
    </style>
    """

st.markdown(get_theme_css(), unsafe_allow_html=True)

db.create_tables()

# ============ SESSION STATE ============
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'theme' not in st.session_state:
    st.session_state['theme'] = "light"

# ============ LOGIN PAGE ============
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #6366F1;'>NexHire Pro</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Enterprise Resume Analysis</h3>", unsafe_allow_html=True)
            st.divider()
            
            tab_sign, tab_reg = st.tabs(["Sign In", "Register"])
            
            with tab_sign:
                st.write("")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.write("")
                if st.button("Sign In", use_container_width=True):
                    if db.login_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['theme'] = db.get_user_theme(username)
                        st.rerun()
                    else:
                        st.error("Access Denied. Invalid credentials.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.write("")
                if st.button("Create Account", use_container_width=True):
                    if new_user and new_pass:
                        if db.add_user(new_user, new_pass):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username already taken.")
                    else:
                        st.warning("Please fill in all fields.")

        st.markdown("<p style='text-align: center; margin-top: 20px; color: #9CA3AF; font-size: 12px;'>© 2025 NexHire Pro</p>", unsafe_allow_html=True)

# ============ MAIN DASHBOARD ============
else:
    # Header
    c_left, c_middle, c_right = st.columns([4, 2, 1])
    
    with c_left:
        st.markdown(f"### Welcome, {st.session_state['username'].title()}")
    
    with c_middle:
        theme_toggle = st.selectbox("Theme", ["Light", "Dark"], index=0 if st.session_state['theme']=="light" else 1, key="theme_select")
        if theme_toggle == "Dark":
            st.session_state['theme'] = "dark"
        else:
            st.session_state['theme'] = "light"
        db.set_user_theme(st.session_state['username'], st.session_state['theme'])
    
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.divider()
    
    # Sidebar Navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "Analyze", "History", "Analytics", "Admin" if db.is_admin(st.session_state['username']) else ""])
    
    # ============ DASHBOARD TAB ============
    if page == "Dashboard":
        history = db.fetch_history(st.session_state['username'])
        last_score = history[0][2] if history else 0
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            with st.container(border=True):
                st.markdown("<div class='metric-label'>Latest Score</div>", unsafe_allow_html=True)
                color = "#10B981" if last_score >= 70 else "#F59E0B" if last_score >= 50 else "#EF4444"
                st.markdown(f"<div style='font-size: 2.5rem; font-weight: 700; color: {color};'>{last_score}%</div>", unsafe_allow_html=True)
        
        with m2:
            with st.container(border=True):
                st.markdown("<div class='metric-label'>Total Analyses</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 2.5rem; font-weight: 700;'>{len(history)}</div>", unsafe_allow_html=True)
        
        with m3:
            with st.container(border=True):
                st.markdown("<div class='metric-label'>Avg Score</div>", unsafe_allow_html=True)
                avg = sum([h[2] for h in history]) / len(history) if history else 0
                st.markdown(f"<div style='font-size: 2.5rem; font-weight: 700;'>{avg:.0f}%</div>", unsafe_allow_html=True)
        
        with m4:
            with st.container(border=True):
                st.markdown("<div class='metric-label'>Status</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 1.5rem;'>Online</div>", unsafe_allow_html=True)
        
        # Score Trend Chart
        if history:
            st.markdown("## Score Trend")
            scores_data = pd.DataFrame([(h[3], h[2]) for h in reversed(history)], columns=['Date', 'Score'])
            fig = px.line(scores_data, x='Date', y='Score', markers=True, title="Your Score History")
            fig.update_layout(hovermode='x unified', template="plotly_dark" if st.session_state['theme']=="dark" else "plotly")
            st.plotly_chart(fig, use_container_width=True)
    
    # ============ ANALYZE TAB ============
    elif page == "Analyze":
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            with st.container(border=True):
                st.markdown("<h2>Resume Upload</h2>", unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf", label_visibility="collapsed")
                
                resume_text = ""
                if uploaded_file:
                    with st.spinner("Extracting text from PDF..."):
                        reader = PyPDF2.PdfReader(uploaded_file)
                        for page in reader.pages:
                            resume_text += page.extract_text()
                    st.success("Resume extracted")
                else:
                    resume_text = st.text_area("Or paste resume text", height=180, placeholder="Paste resume here...", label_visibility="collapsed")
        
        with col_side:
            with st.container(border=True):
                st.markdown("<h2>Job Details</h2>", unsafe_allow_html=True)
                job_role = st.text_input("Position", placeholder="Senior Designer", label_visibility="collapsed")
                job_desc = st.text_area("Description", height=180, placeholder="Paste JD...", label_visibility="collapsed")
        
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            analyze_btn = st.button("Analyze Resume", type="primary", use_container_width=True)
        
        if analyze_btn:
            if resume_text and job_desc:
                with st.spinner("Running AI analysis..."):
                    score = ai.get_ats_score(resume_text, job_desc)
                    feedback = ai.get_feedback(resume_text, job_desc)
                    resume_skills = adv.extract_skills(resume_text)
                    job_skills = adv.extract_skills(job_desc)
                    
                    db.save_scan(st.session_state['username'], job_role, score)
                    db.save_detailed_feedback(st.session_state['username'], job_role, feedback, resume_skills, job_skills)
                
                st.divider()
                
                r1, r2 = st.columns([1, 2])
                with r1:
                    with st.container(border=True):
                        color = "#10B981" if score >= 70 else "#F59E0B" if score >= 50 else "#EF4444"
                        st.markdown(f"<div style='font-size: 64px; font-weight: 700; color: {color}; text-align: center;'>{score}%</div>", unsafe_allow_html=True)
                        status = "Excellent" if score >= 70 else "Moderate" if score >= 50 else "Needs Review"
                        st.markdown(f"<p style='text-align: center;'>{status} Match</p>", unsafe_allow_html=True)
                
                with r2:
                    with st.container(border=True):
                        st.markdown("<h3>AI Assessment</h3>", unsafe_allow_html=True)
                        st.write(feedback)
                
                # Skills Section
                st.markdown("### Skills Analysis")
                s1, s2 = st.columns(2)
                
                with s1:
                    st.markdown("**Matched Skills**")
                    matched = [s for s in resume_skills if s in job_skills]
                    if matched:
                        for skill in matched[:10]:
                            st.markdown(f"✓ {skill}")
                    else:
                        st.markdown("None matched")
                
                with s2:
                    st.markdown("**Missing Skills**")
                    missing = [s for s in job_skills if s not in resume_skills]
                    if missing:
                        for skill in missing[:10]:
                            st.markdown(f"✗ {skill}")
                    else:
                        st.markdown("All skills present!")
                
                # Download Report
                st.markdown("### Download Report")
                pdf_buffer = adv.generate_pdf_report(st.session_state['username'], job_role, score, feedback, resume_skills, job_skills)
                st.download_button("Download PDF Report", pdf_buffer, f"{job_role}_analysis.pdf", "application/pdf")
            else:
                st.warning("Fill in all fields")
    
    # ============ HISTORY TAB ============
    elif page == "History":
        st.markdown("## Scan History")
        all_history = db.fetch_all_history(st.session_state['username'], limit=50)
        
        if all_history:
            df = pd.DataFrame(all_history, columns=['ID', 'Username', 'Job Role', 'Score', 'Date'])
            
            # Filters
            c1, c2 = st.columns(2)
            with c1:
                min_score = st.slider("Min Score", 0, 100, 0)
            with c2:
                max_score = st.slider("Max Score", 0, 100, 100)
            
            filtered_df = df[(df['Score'] >= min_score) & (df['Score'] <= max_score)]
            st.dataframe(filtered_df, use_container_width=True)
            
            # CSV Download
            csv_buffer = adv.generate_csv_report(all_history)
            st.download_button("Download as CSV", csv_buffer, "scan_history.csv", "text/csv")
        else:
            st.info("No scans yet")
    
    # ============ ANALYTICS TAB ============
    elif page == "Analytics":
        st.markdown("## Your Analytics")
        all_history = db.fetch_all_history(st.session_state['username'], limit=100)
        
        if all_history:
            scores = [h[3] for h in all_history]
            stats = adv.calculate_score_stats(scores)
            dist = adv.get_score_distribution(scores)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Average Score", f"{stats['avg']}%")
            m2.metric("Best Score", f"{stats['max']}%")
            m3.metric("Lowest Score", f"{stats['min']}%")
            m4.metric("Total Scans", len(all_history))
            
            st.markdown("### Score Distribution")
            dist_df = pd.DataFrame(list(dist.items()), columns=['Category', 'Count'])
            fig = px.pie(dist_df, values='Count', names='Category', title="Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")
    
    # ============ ADMIN TAB ============
    elif page == "Admin" and db.is_admin(st.session_state['username']):
        st.markdown("## Admin Dashboard")
        
        all_scans = db.get_all_scans()
        if all_scans:
            stats = adv.get_platform_stats(all_scans)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Scans", stats['total_scans'])
            m2.metric("Unique Users", stats['unique_users'])
            m3.metric("Platform Avg", f"{stats['avg_score']}%")
            m4.metric("Best Score", f"{stats['best_score']}%")
            
            st.markdown("### Top Positions")
            top_pos = adv.get_top_positions(all_scans)
            pos_df = pd.DataFrame(top_pos, columns=['Position', 'Count'])
            fig = px.bar(pos_df, x='Position', y='Count', title="Most Analyzed Positions")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### All Scans")
            all_df = pd.DataFrame(all_scans, columns=['ID', 'Username', 'Job Role', 'Score', 'Date'])
            st.dataframe(all_df, use_container_width=True)

