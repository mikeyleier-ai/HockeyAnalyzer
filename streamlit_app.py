import os
import streamlit as st
import yt_dlp

st.title("🏒 AI Hockey Analyzer")

# Selection for input type
input_type = st.radio(
    "Select Video Input:", ["Upload Video", "YouTube Video"], horizontal=True
)

if input_type == "YouTube Video":
    youtube_url = st.text_input(
        "Enter YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    if st.button("Analyze YouTube Video"):
        if youtube_url.strip():
            st.info("Downloading YouTube video...")

            output_file = "downloaded_video.mp4"

            # Clean up old file if it exists
            if os.path.exists(output_file):
                os.remove(output_file)

            # Robust yt-dlp configuration for regular, shorts, and live videos
            ydl_opts = {
                # Try best single MP4 stream, fall back to any best format
                "format": "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "format_sort": ["res", "ext:mp4:m4a"],
                "outtmpl": output_file,
                "overwrites": True,
                "quiet": True,
                "no_warnings": True,
                # Avoid YouTube bot/format blocks
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url.strip()])

                if os.path.exists(output_file):
                    st.success("Video downloaded successfully!")
                    st.video(output_file)

                    # --- Insert your AI video processing call here ---
                    # analyze_video(output_file)
                else:
                    st.error("Download failed to generate video file.")

            except Exception as e:
                st.error(f"Failed to download video: {e}")
        else:
            st.warning("Please enter a valid YouTube URL.")

elif input_type == "Upload Video":
    uploaded_file = st.file_uploader(
        "Choose a video file", type=["mp4", "mov", "avi"]
    )
    if uploaded_file is not None:
        st.video(uploaded_file)

        # Save uploaded file locally for AI model processing
        with open("uploaded_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # --- Insert your AI video processing call here ---
        # analyze_video("uploaded_video.mp4")
