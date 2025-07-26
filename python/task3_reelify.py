import os
import subprocess
import cv2
import streamlit as st
import tempfile

FFMPEG = r"C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
os.environ["FFMPEG_BINARY"] = FFMPEG

st.set_page_config(page_title="Reel Creator", layout="centered")
st.title("3️⃣ Chunk & Evaluate Reel")

uploaded_file = st.file_uploader("Upload a video", type=["mp4"])

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

def resize_video(input_path):
    output_path = input_path.replace(".mp4", "_reel.mp4")
    vf = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    run([FFMPEG, "-y", "-i", input_path, "-vf", vf, "-c:v", "libx264", "-c:a", "copy", output_path])
    return output_path

def chunk_video(input_path):
    base = os.path.basename(input_path).replace(".mp4", "")
    output_pattern = os.path.join("uploads", base + "_part_%03d.mp4")
    run([FFMPEG, "-i", input_path, "-c", "copy", "-map", "0", "-segment_time", "30", "-f", "segment", output_pattern])
    return sorted([os.path.join("uploads", f) for f in os.listdir("uploads") if base in f])

def evaluate_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return {}
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    size = os.path.getsize(path) / (1024 * 1024)
    cap.release()
    return {
        "Resolution": f"{width}x{height}",
        "Duration": round(duration, 2),
        "FPS": round(fps, 2),
        "Size (MB)": round(size, 2)
    }

if uploaded_file:
    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.read())
    st.video(tmp_path)

    if st.button("▶️ Process"):
        reel = resize_video(tmp_path)
        st.success("Reel format ready")
        st.video(reel)

        chunks = chunk_video(reel)
        st.success(f"{len(chunks)} segments created")

        for idx, chunk in enumerate(chunks):
            st.subheader(f"🎞️ Segment {idx+1}")
            st.video(chunk)
            meta = evaluate_video(chunk)
            for k, v in meta.items():
                st.markdown(f"**{k}**: {v}")
