import whisper
import os
import time
import streamlit as st

# ✅ Add FFmpeg to PATH for Whisper (important!)
os.environ["PATH"] += os.pathsep + r"C:/Users/DIVYA SRI/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin"

# ✅ Set up upload folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Transcriber", layout="centered")
st.title("2️⃣ Transcription using Whisper")

# ✅ Upload UI
video_file = st.file_uploader("Upload video for transcription", type=["mp4"])

if video_file:
    # Save uploaded file
    filename = f"video_{int(time.time())}.mp4"
    video_path = r"C:/Reelify/uploads/vv.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    st.success(f"✅ Video saved: {video_path}")

    # Prepare paths
    ffmpeg_path = r"C:/Users/DIVYA SRI/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
    audio_path = r"C:/Reelify/uploads/vv_audio.wav"


    # ✅ Extract audio using full ffmpeg path
    st.info("🔁 Extracting audio...")
    cmd = f'"{ffmpeg_path}" -y -i "{video_path}" -ar 16000 -ac 1 "{audio_path}"'
    result = os.system(cmd)

    if not os.path.exists(audio_path):
        st.error("❌ Audio extraction failed. Please check FFmpeg path and try again.")
        st.code(cmd, language="bash")
    else:
        st.success("✅ Audio extracted successfully.")
        st.audio(audio_path)

        # ✅ Transcribe with Whisper
        st.info("🔁 Transcribing with Whisper...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        full_text = result.get("text", "").strip()

        st.text_area("📝 Transcript", value=full_text, height=300)
        with open(audio_path.replace(".wav", ".txt"), "w", encoding="utf-8") as f:
            f.write(full_text)
        st.download_button("⬇ Download Transcript", full_text, file_name="transcript.txt")
