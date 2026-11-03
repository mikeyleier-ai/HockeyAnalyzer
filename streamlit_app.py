import os
import cv2
import tempfile
import yt_dlp
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Hockey AI Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Hockey AI Analyzer")

st.markdown("""
Analyze hockey videos using Google Gemini.

Supported Inputs:
- Upload MP4, MOV, AVI, MKV
- Paste YouTube links

Analysis Includes:
- Team strategy
- Offensive play
- Defensive play
- Player positioning
- Coaching recommendations
""")

# ==================================================
# GEMINI SETUP
# ==================================================

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
        "gemini-1.5-flash"
    )

except Exception as e:
    st.error(f"Failed to initialize Gemini: {e}")
    st.stop()

# ==================================================
# ANALYSIS PROMPTS
# ==================================================

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
    "Coach Report": """
Act as a hockey coach.

Provide:
- Strengths
- Weaknesses
- Tactical adjustments
- Practice recommendations
""",
    "Player Positioning": """
Analyze player positioning.

Include:
- Offensive positioning
- Defensive positioning
- Support structure
- Spacing
""",
    "Offensive Analysis": """
Analyze offensive execution.

Include:
- Zone entries
- Passing
- Puck support
- Shot selection
""",
    "Defensive Analysis": """
Analyze defensive execution.

Include:
- Coverage
- Gap control
- Defensive support
- Transition defense
"""
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys())
)

prompt = analysis_options[analysis_type]

# ==================================================
# YOUTUBE DOWNLOADER
# ==================================================

def download_youtube(url):

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(
        temp_dir,
        "video.%(ext)s"
    )

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filepath = ydl.prepare_filename(info)

    return filepath

# ==================================================
# FRAME EXTRACTION
# ==================================================

def extract_frames(video_path, max_frames=8):

    frames = []

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return frames

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        return frames

    interval = max(
        total_frames // max_frames,
        1
    )

    current = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        if current % interval == 0:

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frames.append(
                Image.fromarray(rgb_frame)
            )

        current += 1

        if len(frames) >= max_frames:
            break

    cap.release()

    return frames

# ==================================================
# INPUT TABS
# ==================================================

upload_tab, youtube_tab = st.tabs(
    [
        "📹 Upload Video",
        "🔗 YouTube Video"
    ]
)

video_path = None
youtube_url = ""

# ==================================================
# UPLOAD TAB
# ==================================================

with upload_tab:

    uploaded_file = st.file_uploader(
        "Upload Hockey Video",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_file:

        st.video(uploaded_file)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_file:

            temp_file.write(
                uploaded_file.read()
            )

            video_path = temp_file.name

# ==================================================
# YOUTUBE TAB
# ==================================================

with youtube_tab:

    youtube_url = st.text_input(
        "Paste YouTube URL"
    )

    if youtube_url:

        if (
            "youtube.com" in youtube_url
            or "youtu.be" in youtube_url
        ):
            st.video(youtube_url)
        else:
            st.warning(
                "Please enter a valid YouTube URL."
            )

# ==================================================
# ANALYZE
# ==================================================

if st.button(
    "🏒 Analyze Hockey Video",
    type="primary",
    use_container_width=True
):

    try:

        if video_path is None:

            if youtube_url:

                with st.spinner(
                    "Downloading YouTube video..."
                ):

                    try:

                        video_path = download_youtube(
                            youtube_url
                        )

                    except Exception as e:

                        st.error(
                            f"
