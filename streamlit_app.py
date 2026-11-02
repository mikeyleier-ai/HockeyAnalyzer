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
        st.success("App loaded and connected!")
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
    "Analyze the play, positioning, skater speed, and team strategy in this clip."
)

tab1, tab2 = st.tabs(["📹 Upload Video File", "🔗 YouTube Link"])

video_input = None

with tab1:
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
    if uploaded_file:
        video_input = {"type": "file", "data": uploaded_file}

with tab2:
    youtube_url = st.text_input(
        "Paste Public YouTube URL:", 
        placeholder="https://www.youtube.com/watch?v=..."
    )
    if youtube_url:
        video_input = {"type": "youtube", "url": youtube_url}

# ---------------------------------------------------------
# 3. ANALYSIS EXECUTION
# ---------------------------------------------------------

if st.button("Run Hockey Analysis"):
    if not video_input:
        st.warning("Please upload a video file or enter a YouTube URL first.")
    else:
        with st.spinner("Analyzing clip with Gemini..."):
            try:
                contents = []

                if video_input["type"] == "file":
                    # Save uploaded buffer to a temporary file on disk so the API can read it
                    uploaded_file_data = video_input["data"]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file_data.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file_data.getvalue())
                        tmp_path = tmp_file.name

                    # Upload to Gemini File API
                    uploaded_temp = client.files.upload(file=tmp_path)
                    contents.append(uploaded_temp)
                
                elif video_input["type"] == "youtube":
                    # Pass public YouTube URL directly as a file part
                    contents.append(
                        types.Part.from_uri(
                            file_uri=video_input["url"],
                            mime_type="video/*"
                        )
                    )

                # Append prompt text
                contents.append(user_prompt)

                # Generate Content
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents
                )

                st.subheader("Analysis Results:")
                st.write(response.text)

            except Exception as e:
                st.error(f"Error running video analysis: {e}")
