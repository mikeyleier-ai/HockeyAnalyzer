import os
import time
import tempfile
import streamlit as st

from google import genai
from google.genai.errors import APIError

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Hockey Analyzer",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 AI Hockey Video Analyzer")
st.markdown(
    """
Analyze hockey clips using Google's Gemini AI.

Upload a hockey video and receive:
- Play breakdown
- Player positioning
- Offensive strategy
- Defensive coverage
- Strengths and weaknesses
- Coaching recommendations
"""
)

# --------------------------------------------------
# API KEY
# --------------------------------------------------

api_key = None

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found.")
    st.stop()

client = genai.Client(api_key=api_key)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Analysis Options")

analysis_type = st.sidebar.selectbox(
    "Analysis Type",
    [
        "Complete Analysis",
        "Player Positioning",
        "Team Strategy",
        "Offensive Breakdown",
        "Defensive Breakdown",
        "Coach Report"
    ]
)

# --------------------------------------------------
# PROMPTS
# --------------------------------------------------

PROMPTS = {
    "Complete Analysis": """
Analyze this hockey video in detail.

Provide:
1. Play Summary
2. Team Strategy
3. Offensive Structure
4. Defensive Structure
5. Positioning Analysis
6. Notable Strengths
7. Areas for Improvement
8. Coaching Recommendations
""",

    "Player Positioning": """
Analyze all player positioning.

Include:
- Offensive positioning
- Defensive positioning
- Spacing
- Support structure
- Positional mistakes
""",

    "Team Strategy": """
Analyze team tactics and systems.

Include:
- Forecheck
- Backcheck
- Breakouts
- Neutral zone play
- Defensive zone structure
""",

    "Offensive Breakdown": """
Analyze offensive execution.

Include:
- Puck movement
- Cycle game
- Zone entries
- Shot generation
- Offensive support
""",

    "Defensive Breakdown": """
Analyze defensive execution.

Include:
- Coverage
- Gap control
- Defensive support
- Defensive zone structure
- Transition defense
""",

    "Coach Report": """
Create a detailed coaching report.

Include:
- Positive observations
- Required improvements
- Practice recommendations
- Tactical adjustments
"""
}

# --------------------------------------------------
# VIDEO UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Hockey Video",
    type=["mp4", "mov", "avi", "mkv"]
)

if uploaded_file:
    st.video(uploaded_file)

# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if st.button("🏒 Analyze Video", type="primary"):

    if uploaded_file is None:
        st.warning("Please upload a video first.")
        st.stop()

    with st.spinner("Uploading video to Gemini..."):

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as tmp:

                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            uploaded_video = client.files.upload(
                file=temp_path
            )

            progress = st.progress(0)

            while uploaded_video.state.name == "PROCESSING":

                progress.progress(50)

                time.sleep(2)

                uploaded_video = client.files.get(
                    name=uploaded_video.name
                )

            progress.progress(100)

            if uploaded_video.state.name == "FAILED":
                st.error("Video processing failed.")
                st.stop()

        except Exception as e:
            st.error(f"Upload Failed: {e}")
            st.stop()

    with st.spinner("Analyzing hockey footage..."):

        response = None

        models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]

        for model in models:

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=[
                        uploaded_video,
                        PROMPTS[analysis_type]
                    ]
                )

                if response:
                    break

            except APIError as e:

                if getattr(e, "code", None) in [
                    429,
                    500,
                    502,
                    503,
                    504
                ]:

                    time.sleep(5)
                    continue

                raise e

            except Exception:
                continue

        if response:

            st.success("Analysis Complete")

            st.subheader("📋 Hockey Report")

            st.markdown(response.text)

        else:

            st.error(
                "Gemini service unavailable. "
                "Please try again later."
            )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Powered by Google Gemini Flash • Hockey Video Analysis"
)
