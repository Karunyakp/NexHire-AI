import streamlit as st
import database as db
import ai_engine as ai
import PyPDF2
import time

st.set_page_config(page_title="NexHire Enterprise", page_icon="🔹", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .css-card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        padding: 10px 12px;
        font-size: 14px;
        transition: border-color 0.15s ease-in-out;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #0f172a;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border: none;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1e293b;
        transform: translateY(-1px);
    }

    h1 {
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.025em;
    }
    
    h2 {
        font-weight: 600;
        color: #334155;
        letter-spacing: -0.025em;
        font-size: 1.5rem;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """, unsafe_allow_html=True)

db.create_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.write("")
        st.write("")
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>NexHire Enterprise</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Secure AI Assessment Portal</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            st.write("")
            if st.button("Authenticate"):
                if db.login_user(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.rerun()
                else:
                    st.error("Authentication failed.")
        
        with tab2:
            new_user = st.text_input("New Username", key="new_user")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            st.write("")
            if st.button("Create Profile"):
                if new_user and new_pass:
                    if db.add_user(new_user, new_pass):
                        st.success("Profile created.")
                    else:
                        st.error("Username unavailable.")
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown(f"### {st.session_state['username']}")
        st.caption("Standard Access")
        st.markdown("---")
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
        st.markdown("### Audit Log")
        history = db.fetch_history(st.session_state['username'])
        if history:
            for item in history:
                st.markdown(f"""
                <div style="margin-bottom: 12px; font-size: 13px;">
                    <div style="font-weight: 600; color: #334155;">{item[1]}</div>
                    <div style="color: #64748b; display: flex; justify-content: space-between;">
                        <span>{item[3][:10]}</span>
                        <span style="font-weight: 500; color: #0f172a;">{item[2]}%</span>
                    </div>
                </div>
                <hr style="margin: 8px 0; border-top: 1px solid #f1f5f9;">
                """, unsafe_allow_html=True)

    col_header, col_brand = st.columns([3, 1])
    with col_header:
        st.title("Candidate Evaluation")
        st.markdown("<p style='color: #64748b;'>AI-driven competency analysis and ATS compliance check.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h3>Source Document</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                resume_text += page.extract_text()
            st.success("Document parsed successfully.")
        else:
            resume_text = st.text_area("Raw Text Input", height=250, placeholder="Paste candidate resume text here...")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("<h3>Target Profile</h3>", unsafe_allow_html=True)
        job_role = st.text_input("Role Title", placeholder="e.g. Senior Systems Architect")
        job_desc = st.text_area("Job Description", height=250, placeholder="Paste full job requisition here...")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([4, 1])
    with col_r:
        analyze_btn = st.button("Execute Analysis")

    if analyze_btn:
        if resume_text and job_desc:
            with st.spinner("Processing semantics..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.markdown('<div class="css-card" style="border-left: 5px solid #0f172a;">', unsafe_allow_html=True)
                
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    st.markdown("<h3>Compatibility</h3>", unsafe_allow_html=True)
                    color = "#dc2626" if score < 50 else "#16a34a"
                    bg_color = "#fef2f2" if score < 50 else "#f0fdf4"
                    label = "CRITICAL" if score < 50 else "OPTIMAL"
                    
                    st.markdown(f"""
                    <div style="background-color: {bg_color}; padding: 20px; border-radius: 8px; text-align: center;">
                        <div class="metric-value" style="color: {color};">{score}%</div>
                        <div class="status-badge" style="background-color: {color}; color: white;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with res_col2:
                    st.markdown("<h3>Assessment Report</h3>", unsafe_allow_html=True)
                    st.markdown(feedback)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Insufficient data for analysis.")