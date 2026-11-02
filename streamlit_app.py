import streamlit as st
from google import genai

st.title("Hockey Analyzer")

# Initialize Gemini Client directly using Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("App loaded and ready!")
    except Exception as e:
        st.error(f"Error initializing Gemini: {e}")
else:
    st.error("GEMINI_API_KEY missing in Secrets.")

# --- Put your main Hockey Analyzer app features below this line ---
