import streamlit as st
from google import genai

st.title("🏒 Hockey Analyzer")

# 1. SETUP & AUTHENTICATION
if "GEMINI_API_KEY" in st.secrets:
    try:
        # Initialize Gemini Client
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("App loaded and connected!")
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        st.stop()
else:
    st.error("GEMINI_API_KEY missing in Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# 2. YOUR FULL HOCKEY ANALYZER APP LOGIC
# ---------------------------------------------------------

# Example: Video or Prompt Input
user_prompt = st.text_area("Enter play description or analysis query:", "Analyze powerplay setup")
uploaded_file = st.file_uploader("Upload play video or stats CSV", type=["mp4", "mov", "csv"])

if st.button("Run Analysis"):
    with st.spinner("Analyzing with Gemini..."):
        try:
            # Example Gemini call using the official SDK format
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt
            )
            
            st.subheader("Analysis Results:")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Analysis error: {e}")
