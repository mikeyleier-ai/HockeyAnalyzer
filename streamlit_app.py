import streamlit as st
from google import genai

st.title("Hockey Analyzer")

# Safely check if the API key is present in Secrets
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("Gemini API Key connected successfully!")
    except Exception as e:
        st.error(f"Error connecting to Gemini: {e}")
else:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
