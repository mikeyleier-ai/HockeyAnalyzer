import os
import tempfile
import cv2
import streamlit as st
import yt_dlp

st.set_page_config(page_title="AI Hockey Analyzer", page_icon="🏒", layout="wide")


def download_youtube_video(url: str) -> str:
    """Downloads YouTube video or live replay directly to a temporary MP4 file."""
    # Convert /live/ links to standard watch links & strip tracking parameters
    if "/live/" in url:
        video_id = url.split("/live/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    elif "?" in url and "watch" not in url:
        url = url.split("?")[0]

    temp_dir = tempfile.gettempdir()
    out_template = os.path.join(temp_dir, "%(id)s.%(ext)s")

    ydl_opts = {
        # Select single pre-merged format so ffmpeg is not required for merging
        "format": "best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "live_from_start": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


# UI Layout
st.title("🏒 AI Hockey Analyzer")

youtube_url = st.text_input(
    "Enter YouTube Video URL:",
    value="https://www.youtube.com/live/1Mzw8yA5RaY?si=ucEkJAX81zvWgpNP",
    placeholder="https://www.youtube.com/watch?v=...",
)

if st.button("Analyze YouTube Stream Directly"):
    if not youtube_url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Downloading video for processing..."):
            try:
                # 1. Download video to temporary local file
                video_path = download_youtube_video(youtube_url)

                # 2. Open local file in OpenCV
                cap = cv2.VideoCapture(video_path)

                if not cap.isOpened():
                    st.error("Error reading video file with OpenCV.")
                else:
                    st.success("Video loaded successfully! Analyzing frames...")

                    frame_placeholder = st.empty()
                    stop_button = st.button("Stop Analysis")

                    # 3. Read and render frames
                    while cap.isOpened() and not stop_button:
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # --- YOUR AI MODEL INFERENCE HERE ---
                        # Example: frame = your_model.predict(frame)

                        # Convert OpenCV BGR format to RGB for Streamlit displaying
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        frame_placeholder.image(
                            frame_rgb,
                            channels="RGB",
                            use_container_width=True,
                        )

                    cap.release()
                    st.info("Analysis stopped or video ended.")

            except Exception as e:
                st.error(f"Failed to process YouTube video: {str(e)}")
