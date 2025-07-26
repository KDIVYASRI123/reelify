from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import shutil
import subprocess
import tempfile
import time
import cv2
import certifi
import yt_dlp
import whisper
import streamlit as st

# ---------- FFmpeg Setup ----------
FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"  # Make sure this path is valid
if not os.path.isfile(FFMPEG):
    raise RuntimeError("❌ FFMPEG not found at: " + FFMPEG)

os.environ["PATH"] = os.path.dirname(FFMPEG) + os.pathsep + os.environ["PATH"]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Helper to run ffmpeg ----------
def run(cmd: list[str]) -> None:
    print("Running command:", ' '.join(cmd))
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode:
            raise RuntimeError(res.stderr.strip())
    except FileNotFoundError as e:
        raise RuntimeError(f"[FileNotFoundError] Could not run command:\n{' '.join(cmd)}\n\nError: {e}")

# ---------- Audio Extraction (.wav for Whisper) ----------
def extract_audio(inp: str) -> str:
    out = inp.rsplit('.', 1)[0] + "_audio.wav"
    run([FFMPEG, "-y", "-i", inp, "-ar", "16000", "-ac", "1", out])  # mono, 16kHz WAV
    return out

# ---------- Resize Video ----------
def resize_to_reel(inp: str) -> str:
    out = inp.rsplit('.', 1)[0] + "_1080x1920.mp4"
    vf = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    run([FFMPEG, "-y", "-i", inp, "-vf", vf, "-c:v", "libx264", "-c:a", "copy", out])
    return out

# ---------- Download YouTube Video ----------
def download_youtube(url: str) -> str:
    ydl_opts = {
        "format": "best[ext=mp4][acodec!=none][vcodec!=none]",
        "outtmpl": os.path.join(UPLOAD_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "merge_output_format": "mp4",
        "ca_certificates": certifi.where(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        original_path = ydl.prepare_filename(info)
        safe_path = os.path.join(UPLOAD_DIR, f"video_{int(time.time())}.mp4")
        os.rename(original_path, safe_path)
        return safe_path

# ---------- Transcription with Whisper ----------
def transcribe(audio: str) -> tuple[str, str]:
    txt_path = os.path.join(
        UPLOAD_DIR,
        os.path.basename(audio).rsplit('_audio', 1)[0] + "_transcript.txt"
    )

    st.info("🔁 Transcribing using Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio, fp16=False)

    full_text = result.get("text", "").strip()

    if not full_text:
        raise RuntimeError("❌ Whisper failed to transcribe any text.")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return full_text, txt_path

# ---------- Streamlit UI ----------
st.set_page_config(page_title="🎬 Video Processor", layout="centered")
st.title("🎬 Video Processor + Whisper Transcriber")

if "video" not in st.session_state:
    st.session_state.video = None

choice = st.radio("Choose input type", ["Upload", "YouTube"])

# Upload Section
if choice == "Upload":
    f = st.file_uploader("Upload a video (.mp4, .mov, .avi, .mkv)", type=["mp4", "mov", "avi", "mkv"])
    if f:
        filename = f"upload_{int(time.time())}.mp4"
        save_path = os.path.join(UPLOAD_DIR, filename)
        with open(save_path, "wb") as out:
            out.write(f.read())
        st.session_state.video = save_path
        st.success("Uploaded successfully ✅")

# YouTube Section
else:
    url = st.text_input("Enter YouTube video URL")
    if st.button("Download") and url:
        try:
            st.session_state.video = download_youtube(url)
            st.success("Downloaded successfully ✅")
        except Exception as e:
            st.error(f"Download error: {e}")

# Process Section
if st.session_state.video:
    st.video(st.session_state.video)

    if st.button("Process"):
        try:
            video_path = st.session_state.video
            st.caption(f"🎥 Input video: {video_path}")

            audio_path = extract_audio(video_path)
            st.success("✅ Audio extracted")
            st.caption(f"🔊 Audio file: {audio_path}")

            reel_path = resize_to_reel(video_path)
            st.success("✅ Resized to 1080x1920")
            st.caption(f"📱 Reel video: {reel_path}")
            st.video(reel_path)

            text, txt_path = transcribe(audio_path)

            st.success("✅ Transcription complete")
            st.caption(f"📄 Transcript file: {txt_path}")
            st.text_area("📜 Extracted Transcript from Audio", value=text, height=300)

            with open(txt_path, "rb") as f:
                st.download_button("⬇ Download Transcript", f, file_name="transcript.txt")

            with open(reel_path, "rb") as f:
                st.download_button("⬇ Download Resized Reel", f, file_name="reel.mp4")

        except Exception as e:
            st.error(f"❌ Processing error:\n{e}")
