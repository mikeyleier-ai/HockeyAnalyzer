import os
import cv2
import tempfile
import streamlit as st
import yt_dlp
from PIL import Image

from google import genai

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------

st.set_page_config(
    page_title="Hockey AI Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Hockey AI Analyzer")

# ------------------------------------------
# GEMINI
# ------------------------------------------

api_key = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY")
)

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini initialization failed: {e}")
    st.stop()

# ------------------------------------------
# ANALYSIS TYPES
# ------------------------------------------

analysis_options = {
    "Complete Analysis": """
Analyze this hockey video and provide:

1. Play summary
2. Team strategy
3. Offensive analysis
4. Defensive analysis
5. Player positioning
6. Strengths
7. Areas for improvement
8. Coaching recommendations
""",

    "Coach Report": """
Create a coaching report.

Include:
- Strengths
- Weaknesses
- Tactical adjustments
- Practice recommendations
""",

    "Player Positioning": """
Analyze player positioning, support structure,
spacing, and transition play.
"""
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys())
)

prompt = analysis_options[analysis_type]

# ------------------------------------------
# YOUTUBE DOWNLOAD
# ------------------------------------------

def download_youtube(url):

    temp_dir = tempfile.mkdtemp()

    output_file = os.path.join(
        temp_dir,
        "video.%(ext)s"
    )

    options = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_file,
        "noplaylist": True,
        "quiet": True
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        path = ydl.prepare_filename(info)

    return path

# ------------------------------------------
# FRAME EXTRACTION
# ------------------------------------------

def extract_frames(
    video_path,
    max_frames=8
):

    frames = []

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return []

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:
        cap.release()
        return []

    interval = max(
        total_frames // max_frames,
        1
    )

    frame_num = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        if frame_num % interval == 0:

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frames.append(
                Image.fromarray(rgb)
            )

        frame_num += 1

        if len(frames) >= max_frames:
            break

    cap.release()

    return frames

# ------------------------------------------
# INPUT TABS
# ------------------------------------------

tab_upload, tab_youtube = st.tabs(
    [
        "📹 Upload Video",
        "🔗 YouTube Link"
    ]
)

video_path = None
youtube_url = ""

# ------------------------------------------
# FILE UPLOAD
# ------------------------------------------

with tab_upload:

    uploaded_video = st.file_uploader(
        "Upload Hockey Video",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_video:

        st.video(uploaded_video)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_file:

            temp_file.write(
                uploaded_video.read()
            )

            video_path = temp_file.name

# ------------------------------------------
# YOUTUBE INPUT
# ------------------------------------------

with tab_youtube:

    youtube_url = st.text_input(
        "Paste YouTube URL"
    )

    if youtube_url:
        st.video(youtube_url)

# ------------------------------------------
# ANALYZE
# ------------------------------------------

if st.button(
    "🏒 Analyze Hockey Video",
    type="primary"
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
                            f"YouTube download failed: {e}"
                        )

                        st.stop()

            else:

                st.warning(
                    "Upload a video or enter a YouTube URL."
                )

                st.stop()

        with st.spinner(
            "Extracting video frames..."
        ):

            frames = extract_frames(
                video_path
            )

        if not frames:

            st.error(
                "Unable to extract frames from video."
            )

            st.stop()

        with st.spinner(
            "Analyzing video..."
        ):

            content = [prompt]
            content.extend(frames)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=content
            )

        st.success(
            "Analysis Complete ✅"
        )

        st.subheader(
            "🏒 Hockey Analysis Report"
        )

        st.markdown(
            response.text
        )

    except Exception as e:

        st.exception(e)

    finally:

        try:

            if (
                video_path
                and os.path.exists(video_path)
            ):
                os.remove(video_path)

        except Exception:
            pass

# ------------------------------------------
# FOOTER
# ------------------------------------------

st.divider()

st.caption(
    "Powered by Google Gemini"
)
