import os
import time
import tempfile
import streamlit as st
import yt_dlp

from google import genai
from google.genai.errors import APIError

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Hockey Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 AI Hockey Analyzer")

st.markdown("""
Upload a hockey video or paste a YouTube link and receive:

✅ Play Analysis

✅ Team Strategy

✅ Player Positioning

✅ Offensive Zone Breakdown

✅ Defensive Zone Breakdown

✅ Coaching Recommendations
""")

# ---------------------------------------------------------
# GEMINI API
# ---------------------------------------------------------

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Failed to connect to Gemini: {e}")
    st.stop()

# ---------------------------------------------------------
# ANALYSIS TYPES
# ---------------------------------------------------------

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
Analyze all player positioning.

Include:
- Offensive positioning
- Defensive positioning
- Player support
- Spacing
- Mistakes
""",

    "Coach Report": """
Create a professional coaching report.

Include:
- Strengths
- Weaknesses
- Tactical improvements
- Practice recommendations
""",

    "Offensive Analysis": """
Analyze offensive execution.

Include:
- Zone entries
- Puck support
- Passing decisions
- Shot selection
- Offensive systems
""",

    "Defensive Analysis": """
Analyze defensive play.

Include:
- Coverage
- Gap control
- Team structure
- Defensive support
- Transition defense
"""
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys())
)

prompt = analysis_options[analysis_type]

# ---------------------------------------------------------
# YOUTUBE DOWNLOADER
# ---------------------------------------------------------

def download_youtube_video(url):
    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(
        temp_dir,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)

    return file_path

# ---------------------------------------------------------
# INPUT TABS
# ---------------------------------------------------------

tab_upload, tab_youtube = st.tabs(
    ["📹 Upload Video", "🔗 YouTube Video"]
)

video_path = None

# ---------------------------------------------------------
# FILE UPLOAD
# ---------------
