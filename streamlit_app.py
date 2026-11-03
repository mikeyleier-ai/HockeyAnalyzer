import os
import tempfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="AI Hockey Analyzer", page_icon="🏒", layout="wide")

def download_youtube_video(url: str) -> str:
    # Handle /live/ URLs
    if "/live/" in url:
        video_id = url.split("/live/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    temp_dir = tempfile.gettempdir()
    out_template = os.path.join(temp_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        # Select single pre-merged format so ffmpeg is not required
        "format": "best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "live_from_start": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

st.title("🏒 AI Hockey Analyzer")

input_option = st.radio("Select Video Input:", ["Upload Video", "YouTube Video"], horizontal=True)

video_path = None

if input_option == "YouTube Video":
    youtube_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Analyze YouTube Video"):
        if not youtube_url.strip():
            st.error("Please enter a valid YouTube URL.")
        else:
            with st.spinner("Downloading YouTube video..."):
                try:
                    video_path = download_youtube_video(youtube_url)
                    st.success("Download complete!")
                except Exception as e:
                    st.error(f"Failed to download video: {str(e)}")

elif input_option == "Upload Video":
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    if uploaded_file:
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

if video_path and os.path.exists(video_path):
    st.video(video_path)
