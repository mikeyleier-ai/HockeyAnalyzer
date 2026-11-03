import os
import streamlit as st
import yt_dlp

st.title("🏒 AI Hockey Analyzer")

# Create selection for input type
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

            # Options to select the best available format automatically
            ydl_opts = {
                "format": "best",
                "outtmpl": "downloaded_video.mp4",
                "overwrites": True,
                "quiet": True,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])

                st.success("Video downloaded successfully!")

                # Display downloaded video
                st.video("downloaded_video.mp4")

                # --- Put your AI video analysis model call here ---
                # analyze_video("downloaded_video.mp4")

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

        # Save temporary uploaded file for backend processing if needed
        with open("uploaded_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # --- Put your AI video analysis model call here ---
        # analyze_video("uploaded_video.mp4")
