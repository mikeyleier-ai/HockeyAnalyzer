import os
import cv2
import tempfile
import yt_dlp
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Hockey AI Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Hockey AI Analyzer")

st.markdown("""
Upload a hockey video or paste a YouTube link.

The AI can analyze:

• Team strategy  
• Offensive play  
• Defensive play  
• Player positioning  
• Strengths and weaknesses  
• Coaching recommendations
""")

# --------------------------------------------------
# GEMINI SETUP
# --------------------------------------------------

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

try:
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-1.5-flash-latest"
    )

except Exception as e:
    st.error(f"Failed to initialize Gemini: {e}")
    st.stop()

# --------------------------------------------------
# ANALYSIS OPTIONS
# --------------------------------------------------

analysis_options = {
    "Complete Analysis": """
Analyze this hockey video.

Provide:
1. Play Summary
2. Team Strategy
3. Offensive Analysis
4. Defensive Analysis
5. Player Positioning
6. Strengths
7. Weaknesses
8. Coaching Recommendations
""",
    "Player Positioning": """
Analyze player positioning.

Include:
- Offensive positioning
-
