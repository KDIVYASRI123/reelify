import os
import subprocess
import cv2
import streamlit as st
import tempfile

# ----- FFmpeg Setup -----
FFMPEG = r"C:/ffmpeg/bin/ffmpeg.exe"  # ✅ Change if installed elsewhere
os.environ["FFMPEG_BINARY"] = FFMPEG

def run(cmd: list[str]) -> None:
    """Run FFmpeg command and raise error if it fails."""
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        st.error(f"❌ FFmpeg Error:\n{res.stderr}")
        raise RuntimeError(res.stderr.strip())

def resize_to_reel(input_path: str) -> str:
    """Resize input video to vertical 1080x1920 format."""
    output_path = input_path.rsplit('.', 1)[0] + "_reel.mp4"
    vf = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    run([FFMPEG, "-y", "-i", input_path, "-vf", vf, "-c:v", "libx264", "-c:a", "copy", output_path])
    return output_path

def chunk_video(input_path: str, seconds=300) -> list[str]:
    """Split video into chunks of given seconds (default 5 min)."""
    base = os.path.basename(input_path).rsplit('.', 1)[0]
    out_dir = os.path.dirname(input_path)
    out_pattern = os.path.join(out_dir, base + "_part_%03d.mp4")

    run([
        FFMPEG, "-y", "-i", input_path, "-c", "copy", "-map", "0",
        "-segment_time", str(seconds), "-f", "segment", out_pattern
    ])

    return sorted([
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith(base + "_part_") and f.endswith(".mp4")
    ])

def evaluate_video(video_path: str) -> dict:
    """Return resolution, duration, FPS, and size of the video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Failed to open video")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps if fps else 0
    size_MB = os.path.getsize(video_path) / (1024 * 1024)

    cap.release()
    return {
        "Resolution": f"{width}x{height}",
        "Duration (sec)": round(duration, 2),
        "FPS": round(fps, 2),
        "Size (MB)": round(size_MB, 2)
    }

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Video to Reel Creator", layout="centered")
st.title("📽️ Video to Vertical Reel Converter")

uploaded_file = st.file_uploader("📤 Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp:
        tmp.write(uploaded_file.read())
        input_path = tmp.name

    st.video(input_path)

    if st.button("▶️ Process Video"):
        try:
            # Step 1: Resize
            with st.spinner("📐 Resizing to vertical 1080x1920 format..."):
                reel_path = resize_to_reel(input_path)
                st.success("✅ Reel created successfully!")
                st.video(reel_path)

            # Step 2: Split into chunks
            with st.spinner("✂️ Splitting into 5-minute chunks..."):
                chunks = chunk_video(reel_path)
                st.success(f"✅ {len(chunks)} chunk(s) created.")

            # Step 3: Evaluation
            for i, chunk in enumerate(chunks):
                st.subheader(f"🎬 Chunk {i+1}")
                st.video(chunk)
                metrics = evaluate_video(chunk)
                for k, v in metrics.items():
                    st.markdown(f"**{k}**: {v}")

        except Exception as e:
            st.error(f"❌ Processing failed: {e}")
