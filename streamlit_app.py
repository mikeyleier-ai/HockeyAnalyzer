import os
import tempfile
import time
import streamlit as st
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hockey Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 Hockey Analyzer")

# -----------------------------------------------------------------------------
# 1. API Key Initialization
# -----------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing Gemini API Key. Please add `GEMINI_API_KEY` to your Streamlit secrets or environment variables.")
    st.stop()

# Initialize Google GenAI client
client = genai.Client(api_key=api_key)
st.success("App connected to Gemini successfully!")

# -----------------------------------------------------------------------------
# 2. Analysis Prompt Input
# -----------------------------------------------------------------------------
prompt = st.text_area(
    "Analysis Query / Prompt:",
    value="Analyze the play, player positioning, and team strategy in this clip."
)

# -----------------------------------------------------------------------------
# 3. Video Selection (Upload or YouTube)
# -----------------------------------------------------------------------------
tab_upload, tab_youtube = st.tabs(["📹 Upload Video File", "🔗 YouTube Link"])
video_input = None

with tab_upload:
    uploaded_file = st.file_uploader("Upload a hockey clip (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])
    if uploaded_file is not None:
        st.video(uploaded_file)
        # Save uploaded bytes to temporary local file for Gemini Files API
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_filepath = tmp_file.name
        video_input = ("file", tmp_filepath)

with tab_youtube:
    youtube_url = st.text_input(
        "Paste Public YouTube URL:",
        value="https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
    )
    if youtube_url and ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
        st.video(youtube_url)
        video_input = ("youtube", youtube_url)

# -----------------------------------------------------------------------------
# 4. Processing & Model Inference
# -----------------------------------------------------------------------------
if st.button("Run Hockey Analysis", type="primary"):
    if not video_input:
        st.warning("Please upload a video file or provide a valid YouTube URL first.")
    else:
        with st.spinner("Analyzing video clip with Gemini..."):
            try:
                contents = []

                if video_input[0] == "file":
                    # Handle uploaded file via Gemini Files API
                    file_path = video_input[1]
                    uploaded_genai_file = client.files.upload(file=file_path)

                    # Poll until processing completes
                    while uploaded_genai_file.state.name == "PROCESSING":
                        time.sleep(2)
                        uploaded_genai_file = client.files.get(name=uploaded_genai_file.name)

                    if uploaded_genai_file.state.name == "FAILED":
                        st.error("Video processing failed on Google AI servers.")
                        st.stop()

                    contents = [uploaded_genai_file, prompt]

                elif video_input[0] == "youtube":
                    # Explicitly pass video/mp4 MIME type for YouTube URIs
                    yt_part = types.Part.from_uri(
                        file_uri=video_input[1],
                        mime_type="video/mp4"
                    )
                    contents = [yt_part, prompt]

                # Run model generation
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents
                )

                st.subheader("📋 Analysis Results")
                st.write(response.text)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
