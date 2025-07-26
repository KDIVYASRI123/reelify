import streamlit as st
import os

st.set_page_config(page_title="🎬 Reelify App", layout="wide")
st.title("🎬 Reelify - Convert Full Videos to Reels")

st.markdown("### Select a module to run:")

pages = {
    "1️⃣ Upload & Extract Audio": "task1_video_upload.py",
    "2️⃣ Transcribe with Whisper": "task2_transcribe.py",
    "3️⃣ Create Reels": "task3_reelify.py"
}

choice = st.radio("Navigation", list(pages.keys()))

# Debug: show file path being loaded
selected_file = pages[choice]
st.caption(f"Loading: `{selected_file}`")

# ✅ Check if file exists before reading
if not os.path.exists(selected_file):
    st.error(f"❌ File not found: `{selected_file}`")
else:
    with open(selected_file, encoding="utf-8") as f:
        exec(f.read())
