#C:\Users\DIVYA SRI>streamlit run task1.py
import streamlit as st
import subprocess
from pathlib import Path

st.set_page_config(page_title="Video Processor", layout="centered")
st.title("Video Processing & Audio Extractor")

uploaded_file = st.file_uploader(
    "Upload a video file",
    type=["mp4", "mov", "avi", "mkv", "mpeg4"]
)

if uploaded_file:
    # Save the uploaded video
    input_path = "input_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("Video uploaded successfully!")

    # Check if video saved correctly
    if not Path(input_path).exists():
        st.error("File was not saved correctly!")
        st.stop()

    
    audio_output = "audio.wav"
    st.subheader("🎧 Step 1: Extracting Audio")
    audio_cmd = f'ffmpeg -i {input_path} -q:a 0 -map a {audio_output} -y'
    result = subprocess.run(audio_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        st.error("Audio extraction failed:")
        st.code(result.stderr)
    else:
        st.audio(audio_output)
        st.success("Audio extracted successfully.")


    resized_video = "resized_video.mp4"
    st.subheader("Step 2: Resizing to 1080x1920 (Reel format)")
    resize_cmd = (
        f'ffmpeg -i {input_path} '
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


    st.subheader("Step 3: Optional - Chunk Video into 5-minute segments")
    if st.button("Chunk Video"):
        chunk_dir = Path("chunks")
        chunk_dir.mkdir(exist_ok=True)

        chunk_cmd = (
            f'ffmpeg -i {input_path} -c copy -map 0 -segment_time 300 '
            f'-f segment chunks/output%03d.mp4 -y'
        )
        result = subprocess.run(chunk_cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            st.error("Chunking failed:")
            st.code(result.stderr)
        else:
            st.success("Video chunked into 5-minute segments.")







































