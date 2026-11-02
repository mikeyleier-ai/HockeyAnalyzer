import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(page_title="Team Video Analytics", layout="wide")
st.title("🏒 Team Video Breakdown & AI Link Generator")
st.write("Submit a YouTube game link to instantly generate timestamped video clips of Goals, Penalties, and Odd-Man Rushes.")

# 🔒 STEP 1: Add a Security Gate for Your Team
TEAM_PASSWORD = st.sidebar.text_input("🔑 Enter Team Access Code:", type="password")

# Configure the API Key securely from cloud secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("API Key missing. Please configure GEMINI_API_KEY in your deployment panel secrets.")

# Helper to clean the YouTube URL and extract the video ID
def clean_youtube_url(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    # FIXED: Added the explicit watch parameter schema mapping so timestamps parse cleanly on web layout
    return f"https://youtube.com{match.group(1)}" if match else url

# Check security validation parameter before rendering dashboard tools
if not TEAM_PASSWORD:
    st.info("⚠️ Please enter your team's Access Code in the sidebar to unlock the AI analytics tools.")
elif TEAM_PASSWORD != st.secrets.get("TEAM_PASSWORD", "Coach2026"):  # Defaults to Coach2026 if not set in your Streamlit secrets
    st.error("❌ Incorrect Access Code. Please ask your coach for the correct team password.")
else:
    # User Input Form
    video_url = st.text_input("🔗 Paste YouTube Video URL:", placeholder="https://youtube.com...")
    notes = st.text_area("📝 Optional: Add player notes (e.g., 'Look at my gap control on #12 red')", placeholder="Add notes here...")

    if st.button("🚀 Analyze Game & Generate Clips"):
        if not video_url:
            st.warning("Please provide a valid YouTube link.")
        else:
            clean_url = clean_youtube_url(video_url)
            
            with st.spinner("🤖 AI Video Assistant is scanning the tape for clips... Please wait..."):
                try:
                    # Prompt forcing the AI to output clean structured JSON
                    prompt = f"""
                    You are an elite level hockey coach and video coordinator. Analyze the hockey play events occurring in this video: {clean_url}.
                    Identify all instances of:
                    1. Goals Scored
                    2. Penalties Taken
                    3. Odd-Man Rushes (Offensive & Defensive)

                    Additional Player Context: {notes}

                    You must output your response STRICTLY as a raw JSON array matching this format precisely. Do not include markdown wraps or conversational text.
                    [
                      {{"event": "Goal", "timestamp_seconds": 124, "description": "One-timer from the slot after a cross-crease pass."}},
                      {{"event": "Penalty", "timestamp_seconds": 345, "description": "Tripping infraction in the neutral zone."}},
                      {{"event": "Odd-Man Rush (Offensive)", "timestamp_seconds": 512, "description": "3-on-2 rush entry with good support."}}
                    ]
                    """
                    
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(prompt)
                    
                    # Sanitize the AI response string to ensure it's pure JSON
                    raw_text = response.text.strip()
                    
                    # FIXED: Corrected your string split assignments to clean markdown strings securely
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                    elif raw_text.startswith("```"):
                        raw_text = raw_text.split("```")[1].split("```")[0].strip()
                    
                    events = json.loads(raw_text)
                    
                    st.success(f"✅ Analysis Complete! Found {len(events)} key events.")
                    
                    # Display Interactive Links and Feedback side-by-side
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write("### 📺 Embedded Game Tape")
                        st.video(clean_url)
                        
                    with col2:
                        st.write("### ✂️ Auto-Generated Playlists & Feedback")
                        st.write("Click any link below to jump directly to that play on YouTube!")
                        
                    for index, ev in enumerate(events):
                        ev_type = ev.get("event")
                        t_sec = ev.get("timestamp_seconds", 0)
                        desc = ev.get("description", "")
                        
                        # Apply a 10-second buffer so players see the buildup to the play
                        start_time = max(0, t_sec - 10)
                        
                        # Create the exact YouTube timestamp link (t=seconds)
                        clip_link = f"{clean_url}&t={start_time}s"
                        
                        # Format the display clock (MM:SS)
                        mm, ss = divmod(start_time, 60)
                        time_string = f"{mm:02d}:{ss:02d}"
                        
                        # Assign functional visual icons based on event type
                        icon = "🚨" if "Goal" in ev_type else "✖️" if "Penalty" in ev_type else "💨"
                        
                        # Render the clickable button link inside your Google Site
                        with col2:
                            st.markdown(f"#### {icon} {ev_type} ({time_string})")
                            st.write(f"*{desc}*")
                            st.link_button(f"🎬 Watch {ev_type} Clip", clip_link, use_container_width=True)
                            st.divider()
                            
                except json.JSONDecodeError:
                    st.error("The AI generated a response, but it wasn't in the correct format. Please try clicking the button again.")
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")
