import streamlit as st
import subprocess
from pathlib import Path

st.set_page_config(page_title="Video Processor", layout="centered")
st.title("1️⃣ Video Upload & Audio Extraction")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    input_path = "uploads/input_video.mp4"
    Path("uploads").mkdir(exist_ok=True)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("Video uploaded successfully!")

    audio_output = "uploads/audio.wav"
    st.subheader("🎧 Extracting Audio")
    ffmpeg_path = r"C:/Users/DIVYA SRI/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
    audio_cmd = f'"{ffmpeg_path}" -i {input_path} -q:a 0 -map a {audio_output} -y'

    result = subprocess.run(audio_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("Audio extraction failed:")
        st.code(result.stderr)
    else:
        st.audio(audio_output)
        st.success("Audio extracted successfully.")

    resized_video = "uploads/resized_video.mp4"
    st.subheader("📱 Resizing to 1080x1920")
    ffmpeg_path = r"C:/Users/DIVYA SRI/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"

    resize_cmd = (
    f'"{ffmpeg_path}" -i {input_path} '
    f'-vf "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" '
    f'{resized_video} -y'
    )
    result = subprocess.run(resize_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("Video resizing failed:")
        st.code(result.stderr)
    else:
        st.video(resized_video)
        st.success("Video resized successfully.")
