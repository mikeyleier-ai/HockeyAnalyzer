import cv2
import streamlit as st
import yt_dlp

st.set_page_config(page_title="AI Hockey Analyzer", page_icon="🏒", layout="wide")


def get_direct_stream_url(url: str) -> str:
    """Extracts a direct progressive MP4 stream URL from YouTube."""
    # Convert /live/ links to standard watch links
    if "/live/" in url:
        video_id = url.split("/live/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        # Request single progressive MP4 streams that OpenCV can decode natively
        "format": "best[ext=mp4]",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("url")


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
        with st.spinner("Fetching video stream..."):
            try:
                # 1. Fetch direct MP4 stream URL
                stream_url = get_direct_stream_url(youtube_url)

                if not stream_url:
                    st.error("Could not extract a compatible stream format.")
                else:
                    # 2. Pass stream URL to OpenCV
                    cap = cv2.VideoCapture(stream_url)

                    if not cap.isOpened():
                        st.error("OpenCV backend could not open stream format. Try adding 'capfromyoutube' or installing 'opencv-python-headless'.")
                    else:
                        st.success("Connected to stream! Analyzing frames...")

                        frame_placeholder = st.empty()
                        stop_button = st.button("Stop Analysis")

                        # 3. Read and process stream
                        while cap.isOpened() and not stop_button:
                            ret, frame = cap.read()
                            if not ret:
                                break

                            # --- YOUR AI MODEL INFERENCE HERE ---
                            # Example: frame = your_model.predict(frame)

                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                            frame_placeholder.image(
                                frame_rgb,
                                channels="RGB",
                                use_column_width=True,
                            )

                        cap.release()
                        st.info("Analysis stopped or stream ended.")

            except Exception as e:
                st.error(f"Failed to process YouTube stream: {str(e)}")
