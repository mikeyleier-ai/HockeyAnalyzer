import cv2
import streamlit as st
import yt_dlp

st.set_page_config(page_title="AI Hockey Analyzer", page_icon="🏒", layout="wide")


def get_direct_stream_url(url: str) -> str:
    """Extracts a direct stream URL from YouTube without requiring specific extensions."""
    # Clean up /live/ URLs and strip tracking parameters (e.g. ?si=...)
    if "/live/" in url:
        video_id = url.split("/live/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"
    elif "?" in url:
        # Strip query parameters that can interfere with extraction
        url = url.split("?")[0] if "watch" not in url else url

    ydl_opts = {
        # Fall back gracefully across video+audio formats, direct streams, or single files
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "live_from_start": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Extract direct stream URL (handles playability & formats automatically)
        if "url" in info:
            return info["url"]
        elif "requested_formats" in info:
            return info["requested_formats"][0]["url"]
        elif "formats" in info and len(info["formats"]) > 0:
            return info["formats"][-1]["url"]
            
        return None


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
        with st.spinner("Connecting to stream..."):
            try:
                # 1. Extract direct video stream URL
                stream_url = get_direct_stream_url(youtube_url)

                if not stream_url:
                    st.error("Could not extract a stream URL from this video.")
                else:
                    # 2. Connect directly to OpenCV
                    cap = cv2.VideoCapture(stream_url)

                    if not cap.isOpened():
                        st.error("OpenCV could not open the stream. Ensure 'opencv-python-headless' is in requirements.txt.")
                    else:
                        st.success("Connected to stream! Analyzing frames...")

                        frame_placeholder = st.empty()
                        stop_button = st.button("Stop Analysis")

                        # 3. Read and render frames live
                        while cap.isOpened() and not stop_button:
                            ret, frame = cap.read()
                            if not ret:
                                break

                            # --- YOUR AI MODEL INFERENCE HERE ---
                            # Example: frame = your_model.predict(frame)

                            # Convert BGR (OpenCV) to RGB (Streamlit)
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                            frame_placeholder.image(
                                frame_rgb,
                                channels="RGB",
                                use_container_width=True,
                            )

                        cap.release()
                        st.info("Analysis stopped or stream ended.")

            except Exception as e:
                st.error(f"Failed to process YouTube stream: {str(e)}")
