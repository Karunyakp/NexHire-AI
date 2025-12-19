import streamlit as st
import google.generativeai as genai
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="NexHire AI", page_icon="👔", layout="centered")

# --- 1. SMART API CONNECTION FUNCTION ---
# This function loops through all your keys until it finds one that works.
def get_gemini_response(prompt_text):
    # Retrieve all keys from secrets that start with 'GOOGLE_API_KEY'
    # This works for GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc.
    all_keys = [val for key, val in st.secrets.items() if key.startswith("GOOGLE_API_KEY")]
    
    if not all_keys:
        return "❌ Error: No API keys found in .streamlit/secrets.toml"

    # Loop through the keys
    for index, key in enumerate(all_keys):
        try:
            # Configure with the current key
            genai.configure(api_key=key)
            
            # Use Gemini 1.5 Flash (Fast & Efficient)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate the content
            response = model.generate_content(prompt_text)
            
            # If successful, return the text immediately
            return response.text
            
        except Exception as e:
            # If this key fails, print to console and try the next one
            print(f"⚠️ Key #{index+1} failed. Switching to next key... Error: {e}")
            time.sleep(1) # Short pause before switching
            continue

    # If the loop finishes and nothing worked:
    return "❌ Error: All API keys are exhausted or invalid. Please check your billing."

# --- 2. THE UI (USER INTERFACE) ---
st.header("NexHire 👔")
st.subheader("AI-Powered Recruitment Assistant")

# Input Area
user_input = st.text_area("Paste Resume or Job Description here:", height=250, placeholder="Paste text here...")

# Options for the user
task_option = st.selectbox(
    "What should the AI do?",
    [
        "Summarize Candidate Profile",
        "Identify Missing Skills", 
        "Generate Interview Questions",
        "Write a Rejection Email",
        "Match Resume to JD (Paste both above)"
    ]
)

# The Button
if st.button("Analyze Now"):
    if user_input:
        with st.spinner("Processing with Gemini AI..."):
            # Construct a better prompt based on the dropdown selection
            final_prompt = f"Act as an Expert HR Recruiter. Task: {task_option}. \n\nInput Text:\n{user_input}"
            
            # Call the smart function
            result = get_gemini_response(final_prompt)
            
            # Display Result
            st.markdown("### 📝 AI Analysis:")
            st.write(result)
            st.success("Analysis Complete!")
    else:
        st.warning("Please paste some text above first!")

# --- SIDEBAR INFO ---
with st.sidebar:
    st.title("System Status")
    st.info("✅ Multi-Key System Active")
    st.caption("If one API key reaches its limit, NexHire automatically switches to the next available key.")
