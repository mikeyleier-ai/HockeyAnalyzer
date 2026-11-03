import os
import tempfile

import cv2
import streamlit as st
import yt_dlp
import google.generativeai as genai
from PIL import Image

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Hockey AI Analyzer",
    page_icon="🏒",
    layout="wide",
)

st.title("🏒 Hockey AI Analyzer")

# --------------------------------------------------
# GEMINI
# --------------------------------------------------

API_KEY = st.secrets.get(
    "GEMINI_API_KEY",
    os.getenv("GEMINI_API_KEY"),
)

if not API_KEY:
    st.error("GEMINI_API_KEY not configured.")
    st.stop()

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini initialization failed: {e}")
    st.stop()

# --------------------------------------------------
# ANALYSIS TYPES
# --------------------------------------------------

analysis_options = {
    "Complete Analysis": """
Analyze the hockey clip and provide:

1. Play summary
2. Team strategy
3. Offensive analysis
4. Defensive analysis
5. Player positioning
6. Strengths
7. Weaknesses
8. Coaching recommendations
""",
    "Coach Report": """
Create a coaching report with:

- Strengths
- Areas for improvement
- Tactical adjustments
- Practice recommendations
""",
    "Player Positioning": """
Analyze player positioning and support structure.
""",
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys()),
)

prompt = analysis_options[analysis_type]

# --------------------------------------------------
# YOUTUBE DOWNLOAD
# --------------------------------------------------

def download_youtube(url):

    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": os.path.join(
            temp_dir,
            "video.%(ext)s"
        ),
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            url,
            download=True,
        )

        file_path = ydl.prepare_filename(info)

    return file_path

# --------------------------------------------------
# FRAME EXTRACTION
# --------------------------------------------------

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
        1,
    )

    frame_count = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        if frame_count % interval == 0:

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            frames.append(
                Image.fromarray(rgb)
            )

        frame_count += 1

        if len(frames) >= max_frames:
            break

    cap.release()

    return frames

# --------------------------------------------------
# INPUT
# --------------------------------------------------

tab_upload, tab_youtube = st.tabs(
    ["📹 Upload Video", "🔗 YouTube"]
)

video_path = None
youtube_url = ""

with tab_upload:

    uploaded_file = st.file_uploader(
        "Upload Hockey Video",
        type=["mp4", "mov", "avi", "mkv"],
    )

    if uploaded_file:

        st.video(uploaded_file)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4",
        ) as tmp:

            tmp.write(uploaded_file.read())
            video_path = tmp.name

with tab_youtube:

    youtube_url = st.text_input(
        "Paste YouTube URL"
    )

    if youtube_url:
        st.video(youtube_url)

# --------------------------------------------------
# ANALYZE
# --------------------------------------------------

if st.button(
    "🏒 Analyze Hockey Video",
    type="primary",
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
                    "Upload a video or provide a YouTube URL."
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
                "Unable to extract frames."
            )

            st.stop()

        with st.spinner(
            "Analyzing hockey footage..."
        ):

            content = [prompt]
            content.extend(frames)

            response = model.generate_content(
                content
            )

        st.success(
            "Analysis Complete ✅"
        )

        if hasattr(response, "text"):
            st.markdown(response.text)
        else:
            st.write(response)

    except Exception as e:

        st.exception(e)

    finally:

        if (
            video_path
            and os.path.exists(video_path)
        ):
            try:
                os.remove(video_path)
            except Exception:
                pass

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Powered by Google Gemini"
)
