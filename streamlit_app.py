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

st.markdown(
    """
Upload a hockey clip or paste a YouTube link.

The AI will analyze:

- Team strategy
- Player positioning
- Offensive play
- Defensive play
- Strengths
- Weaknesses
- Coaching recommendations
"""
)

# --------------------------------------------------
# GEMINI SETUP
# --------------------------------------------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found.")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini initialization failed: {e}")
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
- Defensive positioning
- Support structure
- Spacing
- Errors
""",
    "Coach Report": """
Create a coaching report.

Include:
- Positive observations
- Areas to improve
- Tactical adjustments
- Practice recommendations
""",
    "Offensive Analysis": """
Analyze offensive execution.

Include:
- Puck support
- Passing options
- Shot selection
- Zone entries
""",
    "Defensive Analysis": """
Analyze defensive execution.

Include:
- Coverage
- Gap control
- Transition defense
- Team support
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
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        file_path = ydl.prepare_filename(info)

        if not file_path.endswith(".mp4"):
            file_path = os.path.splitext(file_path)[0] + ".mp4"

    return file_path

# --------------------------------------------------
# FRAME EXTRACTION
# --------------------------------------------------

def extract_frames(video_path, max_frames=8):

    frames = []

    cap = cv2.VideoCapture(video_path)

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
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
    ["📹 Upload Video", "🔗 YouTube"]
)

video_path = None
youtube_url = ""

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

with tab1:

    uploaded_video = st.file_uploader(
        "Upload Hockey Video",
        type=["mp4", "mov", "avi", "mkv"]
    )

    if uploaded_video:

        st.video(uploaded_video)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_video:

            temp_video.write(
                uploaded_video.read()
            )

            video_path = temp_video.name

# --------------------------------------------------
# YOUTUBE
# --------------------------------------------------

with tab2:

    youtube_url = st.text_input(
        "Paste a YouTube URL"
    )

    if youtube_url:
        st.video(youtube_url)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if st.button(
    "🏒 Analyze Hockey Video",
    use_container_width=True,
    type="primary"
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
                    "Please upload a video or paste a YouTube URL."
                )

                st.stop()

        with st.spinner(
            "Extracting video frames..."
        ):

            frames = extract_frames(
                video_path,
                max_frames=8
            )

        if len(frames) == 0:

            st.error(
                "Unable to extract frames from the video."
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

        st.success(
            "Analysis Complete ✅"
        )

        st.subheader(
            "🏒 Hockey Analysis"
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
    "Powered by Google Gemini Vision"
)
