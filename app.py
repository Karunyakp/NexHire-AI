import streamlit as st
import pandas as pd
import database as db
import ai_engine as ai
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
        
        /* Sidebar Links */
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

        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #FFFFFF;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 14px;
        }

        div.stButton > button {
            background-color: #4F46E5;
            color: white;
            border-radius: 8px;
            padding: 14px 28px;
            font-weight: 600;
            border: none;
            width: 100%;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background-color: #4338ca;
            transform: translateY(-2px);
        }
        
        #MainMenu, footer, header {visibility: hidden;}
        div[data-testid="stHeaderActionElements"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (GLOBAL PROOF) ---
def render_sidebar():
    with st.sidebar:
        try:
            st.image("logo.png", width=80) 
        except:
            pass 
            
        st.title("NexHire")
        st.markdown("### Enterprise Recruitment Intelligence")
        
        st.divider()
        
        st.subheader("Connect with Developer")
        st.link_button("🔗 LinkedIn Profile", "https://www.linkedin.com/in/karunyakp")
        st.link_button("💻 GitHub Profile", "https://github.com/karunyakp")
        
        st.write("") 
        st.divider()
        
        st.caption("Developed & Maintained by")
        st.markdown("### Karunya. K. P") 
        st.caption("© 2025 NexHire Systems")

# --- 3. LOGIN PAGE ---
def login_page():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.write("")
        st.write("")
        
        with st.container(border=True):
            # Logo centered
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                try:
                    st.image("logo.png", use_container_width=True)
                except:
                    st.markdown("<h1 style='text-align: center; color: #4F46E5;'>NexHire</h1>", unsafe_allow_html=True)

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
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
            
            with tab_reg:
                st.write("")
                new_user = st.text_input("Choose Username", key="new_user")
                new_pass = st.text_input("Choose Password", type="password", key="new_pass")
                st.info("ℹ️ Password must be at least 8 characters.")
                
                st.write("")
                if st.button("Create Profile"):
                    if new_user and new_pass:
                        # 1. Enforce Password Length
                        if len(new_pass) < 8:
                            st.error("❌ Password is too short! Must be at least 8 characters.")
                        else:
                            # 2. Attempt Registration
                            if db.add_user(new_user, new_pass):
                                # 3. CHECK FOR ADMIN (Karunya)
                                if new_user.lower() == "karunya":
                                    db.set_admin(new_user)
                                    st.success("👑 Admin Account Created! You have special access.")
                                else:
                                    st.success("Account created! Please log in.")
                            else:
                                st.error("Username already taken.")
                    else:
                        st.warning("Please fill all fields.")

            # Footer Proof
            st.write("")
            st.divider()
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.caption("Application Developed by")
            st.markdown("**Karunya. K. P**") 
            st.caption("© 2025 NexHire Systems")
            st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DASHBOARD PAGE ---
def dashboard_page():
    # Header
    c_left, c_right = st.columns([6, 1])
    with c_left:
        cl1, cl2 = st.columns([1, 10])
        with cl1:
            try:
                st.image("logo.png", width=50)
            except:
                st.write("🔹")
        with cl2:
            st.markdown(f"### Hello, {st.session_state['username']}")
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin-top: -15px;'>Your recruitment analytics overview</p>", unsafe_allow_html=True)
            
    with c_right:
        if st.button("Sign Out"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    st.divider()

    # --- 🔐 ADMIN CONSOLE (Only for Karunya/Admins) ---
    if db.is_admin(st.session_state['username']):
        st.markdown("### 🛡️ Admin Surveillance Console")
        st.info("You are viewing this because you are an Administrator.")
        
        with st.expander("View All User Uploads & Results", expanded=True):
            # Fetch all history from DB
            all_data = db.get_all_scans()
            if all_data:
                # Create a clean table
                df = pd.DataFrame(all_data, columns=['ID', 'User', 'Uploaded Role (Job)', 'Result (Score)', 'Date'])
                # Hide ID column for cleaner look
                st.dataframe(df[['Date', 'User', 'Uploaded Role (Job)', 'Result (Score)']], use_container_width=True)
            else:
                st.warning("No data found in the system yet.")
        st.divider()
    # ----------------------------------------------------

    # User Metrics
    history = db.fetch_history(st.session_state['username'])
    last_score = history[0][2] if history else 0
    
    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.markdown("### LATEST SCORE")
            st.markdown(f"<h1 style='margin: 0; color: #4F46E5;'>{last_score}%</h1>", unsafe_allow_html=True)
    with m2:
        with st.container(border=True):
            st.markdown("### TOTAL SCANS")
            st.markdown(f"<h1 style='margin: 0; color: #111827;'>{len(history)}</h1>", unsafe_allow_html=True)
    with m3:
        with st.container(border=True):
            st.markdown("### SYSTEM STATUS")
            st.markdown(f"<h1 style='margin: 0; color: #10B981;'>Online</h1>", unsafe_allow_html=True)

    st.write("")
    
    # Input Area
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        with st.container(border=True):
            st.markdown("### 1. Document Processing")
            st.info("Upload the candidate's PDF resume here.")
            uploaded_file = st.file_uploader("Upload PDF", type="pdf", label_visibility="collapsed")
            
            resume_text = ""
            if uploaded_file:
                with st.spinner("Extracting text..."):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages:
                        resume_text += page.extract_text()
                st.success("Resume Extracted Successfully")
            else:
                resume_text = st.text_area("Or paste raw text", height=200, placeholder="Paste resume content here...")

    with col_side:
        with st.container(border=True):
            st.markdown("### 2. Job Requisition")
            job_role = st.text_input("Role Title", placeholder="e.g. Product Designer")
            job_desc = st.text_area("Requirements", height=250, placeholder="Paste Job Description here...", label_visibility="collapsed")

    st.write("")
    
    # AI Engine Trigger
    if st.button("Initialize Intelligence Engine", type="primary"):
        if resume_text and job_desc:
            with st.spinner("Analyzing candidate profile against requirements..."):
                time.sleep(1)
                score = ai.get_ats_score(resume_text, job_desc)
                feedback = ai.get_feedback(resume_text, job_desc)
                
                # Save scan results to DB
                db.save_scan(st.session_state['username'], job_role, score)
                
                st.divider()
                
                r1, r2 = st.columns([1, 2])
                with r1:
                    with st.container(border=True):
                        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.markdown("### COMPATIBILITY")
                        color = "#EF4444" if score < 50 else "#4F46E5"
                        st.markdown(f"<h1 style='font-size: 72px; color: {color}; margin: 0;'>{score}%</h1>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with r2:
                    with st.container(border=True):
                        st.markdown("### AI ASSESSMENT REPORT")
                        st.write(feedback)
        else:
            st.warning("⚠️ Please provide both a Resume and a Job Description.")

# --- 5. MAIN EXECUTION ---
def main():
    setup_page()
    db.create_tables()
    
    # Always render sidebar
    render_sidebar()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""

    if not st.session_state['logged_in']:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
