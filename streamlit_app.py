import os
import tempfile
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Hockey Analyzer", page_icon="🏒")
st.title("🏒 Hockey Analyzer")

# 1. SETUP & AUTHENTICATION
if "GEMINI_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("App connected to Gemini successfully!")
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")
        st.stop()
else:
    st.error("GEMINI_API_KEY missing in Streamlit Secrets.")
    st.stop()

# ---------------------------------------------------------
# 2. INPUT SELECTION (File Upload or YouTube Link)
# ---------------------------------------------------------

user_prompt = st.text_area(
    "Analysis Query / Prompt:", 
    "Analyze the play, player positioning, puck movement, and team strategy in this video."
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
    youtube_url = st.text_input(
        "Paste Public YouTube URL:", 
        placeholder="https://www.youtube.com/watch?v=..."
    )
    if youtube_url.strip():
        video_type = "youtube"

# ---------------------------------------------------------
# 3. ANALYSIS EXECUTION
# ---------------------------------------------------------

if st.button("Run Hockey Analysis"):
    if not video_type:
        st.warning("Please upload a video file or enter a valid YouTube URL first.")
    else:
        with st.spinner("Processing video with Gemini..."):
            tmp_path = None
            try:
                contents = []

                if video_type == "file":
                    # Save stream to temporary file on disk
                    file_ext = uploaded_file.name.split(".")[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # Upload temporary file to Gemini Files API
                    uploaded_temp = client.files.upload(file=tmp_path)
                    contents.append(uploaded_temp)
                
                elif video_type == "youtube":
                    # Standard structure for YouTube URL inputs
                    contents.append(
                        types.Part(
                            file_data=types.FileData(
                                file_uri=youtube_url.strip()
                            )
                        )
                    )

                # Append prompt text
                contents.append(user_prompt)

                # Call model
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )

                st.subheader("Analysis Results:")
                st.write(response.text)

            except Exception as e:
                st.error(f"Error running video analysis: {e}")
            
            finally:
                # Clean up local temporary file if it was created
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)
