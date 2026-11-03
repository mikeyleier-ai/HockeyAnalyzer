import streamlit as st
import yt_dlp
import os

st.title("🏒 AI Hockey Analyzer")

# Create tabs or a radio selection for input type
input_type = st.radio("Select Video Input:", ["Upload Video", "YouTube Video"], horizontal=True)

if input_type == "YouTube Video":
    youtube_url = st.text_input("Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("Analyze YouTube Video"):
        if youtube_url.strip():
            st.info("Downloading YouTube video...")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Download best quality mp4
                'outtmpl': 'downloaded_video.mp4',  # Save filename
                'overwrites': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                
                st.success("Video downloaded successfully!")
                
                # Display the downloaded video in Streamlit
                st.video("downloaded_video.mp4")
                
                # --- Insert your AI analysis function here ---
                # analyze_video("downloaded_video.mp4")
                
            except Exception as e:
                st.error(f"Failed to download video: {e}")
        else:
            st.warning("Please enter a valid YouTube URL.")

elif input_type == "Upload Video":
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
    if uploaded_file is not None:
        st.video(uploaded_file)
        # --- Insert your AI analysis function here ---
