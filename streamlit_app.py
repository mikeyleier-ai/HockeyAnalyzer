import os
import cv2
import yt_dlp
import tempfile
import streamlit as st
import google.generativeai as genai

from PIL import Image

# ------------------------------------------
# PAGE SETUP
# ------------------------------------------

st.set_page_config(
    page_title="🏒 Hockey Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 AI Hockey Analyzer")

# ------------------------------------------
# GEMINI
# ------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# ------------------------------------------
# ANALYSIS TYPES
# ------------------------------------------

analysis_options = {
    "Complete Analysis":
    """
    Analyze this hockey play.

    Include:

    - Play summary
    - Team strategy
    - Offensive positioning
    - Defensive positioning
    - Key strengths
    - Areas for improvement
    - Coaching recommendations
    """,

    "Coach Report":
    """
    Produce a detailed coaching report.

    Include:

    - Positive habits
    - Tactical mistakes
    - Team systems
    - Skill development recommendations
    """,

    "Player Positioning":
    """
    Analyze positioning.

    Include:

    - Spacing
    - Support
    - Defensive coverage
    - Offensive support
    """
}

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    list(analysis_options.keys())
)

analysis_prompt = analysis_options[
    analysis_type
]

# ------------------------------------------
# YOUTUBE DOWNLOAD
# ------------------------------------------

def download_youtube(url):

    temp_folder = tempfile.mkdtemp()

    output_file = os.path.join(
        temp_folder,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "mp4",
        "outtmpl": output_file,
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(
        ydl_opts
    ) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        video_file = ydl.prepare_filename(
            info
        )

    return video_file

# ------------------------------------------
# EXTRACT FRAMES
# ------------------------------------------

def extract_frames(
    video_path,
    max_frames=8
):

    frames = []

    cap = cv2.VideoCapture(
        video_path
    )

    frame_count = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if frame_count == 0:
        return frames

    step = max(
        frame_count // max_frames,
        1
    )

    count = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if count % step == 0:

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frames.append(
                Image.fromarray(rgb)
            )

        count += 1

        if len(frames) >= max_frames:
            break

    cap.release()

    return frames

# ------------------------------------------
# INPUT
# ------------------------------------------

tab1, tab2 = st.tabs(
    [
        "Upload Video",
        "YouTube Video"
    ]
)

video_file_path = None

with tab1:

    uploaded_video = st.file_uploader(
        "Upload Hockey Clip",
        type=[
            "mp4",
            "mov",
            "avi",
            "mkv"
        ]
    )

    if uploaded_video:

        st.video(
            uploaded_video
        )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_file:

            temp_file.write(
                uploaded_video.read()
            )

            video_file_path = (
                temp_file.name
            )

with tab2:

    youtube_url = st.text_input(
        "Paste YouTube URL"
    )

    if youtube_url:

        st.video(
            youtube_url
        )

# ------------------------------------------
# ANALYZE BUTTON
# ------------------------------------------

if st.button(
    "🏒 Analyze Hockey Video"
):

    try:

        if not video_file_path:

            if youtube_url:

                with st.spinner(
                    "Downloading YouTube video..."
                ):

                    video_file_path = (
                        download_youtube(
                            youtube_url
                        )
                    )

            else:

                st.warning(
                    "Upload a video or provide a YouTube URL."
                )

                st.stop()

        with st.spinner(
            "Extracting frames..."
        ):

            frames = extract_frames(
                video_file_path,
                max_frames=8
            )

        if len(frames) == 0:

            st.error(
                "No frames extracted."
            )

            st.stop()

        with st.spinner(
            "Analyzing hockey footage..."
        ):

            content = [
                analysis_prompt
            ]

            for frame in frames:

                content.append(
                    frame
                )

            response = (
                model.generate_content(
                    content
                )
            )

        st.success(
            "Analysis Complete"
        )

        st.subheader(
            "🏒 Hockey Report"
        )

        st.markdown(
            response.text
        )

    except Exception as e:

        st.exception(e)

# ------------------------------------------
# FOOTER
# ------------------------------------------

st.divider()

st.caption(
    "Powered by Gemini Vision"
)
