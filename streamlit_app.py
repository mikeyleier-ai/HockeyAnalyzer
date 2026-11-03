import cv2
import streamlit as st
import yt_dlp

st.set_page_config(page_title="AI Hockey Analyzer", page_icon="🏒", layout="wide")


def stream_youtube_frames(url: str):
    """Fetches the direct stream URL using yt-dlp without downloading the file."""
    # Convert /live/ links to standard watch links
    if "/live/" in url:
        video_id = url.split("/live/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        # Select best available pre-merged video/stream format
        "format": "best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # download=False keeps it in memory
        stream_url = info.get("url")
        return stream_url


# UI Layout
st.title("🏒 AI Hockey Analyzer")

youtube_url = st.text_input(
    "Enter YouTube Video URL:",
    value="https://www.youtube.com/watch?v=1Mzw8yA5RaY",
    placeholder="https://www.youtube.com/watch?v=...",
)

if st.button("Analyze YouTube Stream Directly"):
    if not youtube_url.strip():
        st.error("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Connecting to stream..."):
            try:
                # 1. Get direct video stream URL
                direct_stream_url = stream_youtube_frames(youtube_url)

                # 2. Open stream directly in OpenCV
                cap = cv2.VideoCapture(direct_stream_url)

                if not cap.isOpened():
                    st.error("Error opening video stream.")
                else:
                    st.success("Connected to stream! Analyzing frames...")

                    # Frame placeholder for rendering live inferences in Streamlit
                    frame_placeholder = st.empty()
                    stop_button = st.button("Stop Analysis")

                    # 3. Read and process stream frame-by-frame
                    while cap.isOpened() and not stop_button:
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # --- YOUR AI MODEL INFERENCE HERE ---
                        # Example: frame = your_model.predict(frame)
                        # OpenCV reads in BGR format; convert to RGB for Streamlit displaying
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # Display current frame in app
                        frame_placeholder.image(
                            frame_rgb,
                            channels="RGB",
                            use_column_width=True,
                        )

                    cap.release()
                    st.info("Analysis stopped or stream ended.")

            except Exception as e:
                st.error(f"Failed to process YouTube stream: {str(e)}")
