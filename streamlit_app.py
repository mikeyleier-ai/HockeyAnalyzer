import os
import tempfile
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Hockey Analyzer", page_icon="🏒")
st.title("🏒 Hockey Analyzer")

# 1. READ THE SECRET KEY
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")
    st.stop()

# Build the Gemini Client using the key
client = genai.Client(api_key=api_key)
st.success("App connected to Gemini successfully!")

# 2. INPUT SELECTION
user_prompt = st.text_area(
    "Analysis Query / Prompt:", 
    "Analyze the play, player positioning, and team strategy in this clip."
)

tab1, tab2 = st.tabs(["📹 Upload Video File", "🔗 YouTube Link"])

video_type = None
uploaded_file = None
youtube_url = ""

with tab1:
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
    if uploaded_file:
        video_type = "file"

with tab2:
    youtube_url = st.text_input("Paste Public YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    if youtube_url.strip():
        video_type = "youtube"

# 3. RUN ANALYSIS
if st.button("Run Hockey Analysis"):
    if not video_type:
        st.warning("Please upload a video file or enter a YouTube link first.")
    else:
        with st.spinner("Analyzing with Gemini..."):
            tmp_path = None
            try:
                contents = []

                if video_type == "file":
                    # Save video to a temporary file for processing
                    file_ext = uploaded_file.name.split(".")[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    uploaded_temp = client.files.upload(file=tmp_path)
                    contents.append(uploaded_temp)

                elif video_type == "youtube":
                    # Send YouTube URL directly to Gemini
                    contents.append(
                        types.Part.from_uri(
                            file_uri=youtube_url.strip(),
                            mime_type="video/*"
                        )
                    )

                contents.append(user_prompt)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )

                st.subheader("Analysis Results:")
                st.write(response.text)

            except Exception as e:
                st.error(f"Error: {e}")

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
