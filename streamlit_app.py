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
    page_title="🏒 Hockey AI Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Hockey AI Analyzer")

st.markdown("""
Upload a hockey video or paste a YouTube link.

The AI can analyze:

- Team systems
- Offensive play
- Defensive structure
- Player positioning
- Strengths and weaknesses
- Coaching recommendations
""")

# --------------------------------------------------
# GEMINI SETUP
# --------------------------------------------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY was not found.")
    st.stop()

try:
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        "gemini-1.5-flash"
    )

except Exception as e:
    st.error(
        f"Failed to initialize Gemini: {e}"
    )
    st.stop()

# --------------------------------------------------
# ANALYSIS MODES
# --------------------------------------------------

analysis_options = {
    "Complete Analysis": """
Analyze this hockey video.

Include:

1. Play Summary
2. Team Strategy
3. Offensive Analysis
4. Defensive Analysis
5. Positioning
6. Strengths
7. Weaknesses
8. Coaching Recommendations
""",

    "Coach Report": """
Create a detailed hockey coaching report.

Include:

- Positive habits
- Tactical concerns
- Team systems
- Practice recommendations
""",

    "Player Positioning": """
Analyze player positioning.

Include:

- Offensive spacing
- Defensive spacing
- Support structure
- Transition positioning
- Positioning errors
""",

    "Offensive Analysis": """
Analyze offensive execution.

Include:

- Zone entries
- Passing
- Puck support
- Shot opportunities
- Offensive decision making
""",

    "Defensive Analysis": """
Analyze defensive execution.

Include:

- Gap control
- Coverage
- Defensive support
- Defensive zone structure
- Transition defense
"""
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys())
)

prompt = analysis_options[analysis_type]

# --------------------------------------------------
# YOUTUBE DOWNLOAD
# --------------------------------------------------

def download_youtube(url):

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(
        temp_dir,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        file_path = ydl.prepare_filename(
            info
        )

    return file_path

# --------------------------------------------------
# FRAME EXTRACTION
# --------------------------------------------------

def extract_frames(
    video_path,
    max_frames=10
):

    frames = []

    cap = cv2.VideoCapture(
        video_path
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if total_frames <= 0:
        cap.release()
        return []

    step_size = max(
        total_frames // max_frames,
        1
    )

    frame_num = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        if frame_num % step_size == 0:

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

# --------------------------------------------------
# INPUT TABS
# --------------------------------------------------

tab1, tab2 = st.tabs(
    [
        "📹 Upload Video",
        "🔗 YouTube"
    ]
)

video_path = None
youtube_url = ""

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

with tab1:

    uploaded_video = st.file_uploader(
        "Upload Hockey Video",
        type=[
            "mp4",
            "mov",
            "avi",
            "mkv"
        ]
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

# --------------------------------------------------
# YOUTUBE INPUT
# --------------------------------------------------

with tab2:

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

# --------------------------------------------------
# ANALYZE BUTTON
# --------------------------------------------------

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

                    video_path = download_youtube(
                        youtube_url
                    )

            else:

                st.warning(
                    "Upload a video or paste a YouTube URL."
                )
                st.stop()

        with st.spinner(
            "Extracting frames..."
        ):

            frames = extract_frames(
                video_path,
                max_frames=10
            )

        if len(frames) == 0:

            st.error(
                "No frames could be extracted from this video."
            )
            st.stop()

        with st.spinner(
            "Analyzing hockey footage..."
        ):

            content = [prompt]

            for frame in frames:
                content.append(frame)

            response = model.generate_content(
                content
            )

            if (
                not response
                or not hasattr(response, "text")
            ):
                raise Exception(
                    "Gemini returned an empty response."
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

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Powered by Google Gemini 1.5 Flash"
)
``
