import streamlit as st
import os
from pathlib import Path
import tempfile
import warnings

# ✅ Add FFmpeg directory to system PATH
os.environ["PATH"] += os.pathsep + r"C:\Users\DIVYA SRI\Reelify\ffmpeg\bin"

from video_processor import VideoProcessor
from auth import AuthManager
from database import init_database
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

import whisper
model = whisper.load_model("base")

# Initialize database
init_database()

# Flask app setup (optional, for API)
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Initialize components
auth_manager = AuthManager()
video_processor = VideoProcessor()

# Page configuration
st.set_page_config(
    page_title="Video to Reels Converter",
    page_icon="🎬",
    layout="wide"
)

def main():
    st.title("🎬 Video to Reels Converter")
    st.markdown("Transform your videos into engaging 30-second reels using AI")

    # Session state init
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    # Auth routing
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if auth_manager.authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email")
            submit = st.form_submit_button("Register")

            if submit:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif auth_manager.register_user(new_username, new_password, email):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")

def show_main_app():
    # Sidebar
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.username}!")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

        st.markdown("---")
        st.markdown("### How it works:")
        st.markdown("1. Upload your video")
        st.markdown("2. AI extracts and analyzes audio")
        st.markdown("3. Important segments are identified")
        st.markdown("4. 30-second reels are generated")

    # Main content
    st.subheader("Upload Video for Reel Generation")

    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Upload a video file to convert into reels"
    )

    if uploaded_file is not None:
        st.video(uploaded_file)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / (1024*1024):.2f} MB")

        with col2:
            reel_count = st.number_input("Number of reels to generate", min_value=1, max_value=5, value=2)
            reel_duration = st.number_input("Reel duration (seconds)", min_value=15, max_value=60, value=30)

        if st.button("Generate Reels", type="primary"):
            with st.spinner("Processing video... This may take a few minutes."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        temp_path = tmp_file.name

                    # Process video
                    result = video_processor.process_video(
                        temp_path,
                        reel_count=reel_count,
                        reel_duration=reel_duration
                    )

                    if result['success']:
                        st.success("Reels generated successfully!")
                        st.subheader("Generated Reels")

                        for i, reel_path in enumerate(result['reels']):
                            st.write(f"**Reel {i+1}**")
                            st.video(reel_path)
                            with open(reel_path, 'rb') as f:
                                st.download_button(
                                    label=f"Download Reel {i+1}",
                                    data=f.read(),
                                    file_name=f"reel_{i+1}.mp4",
                                    mime="video/mp4"
                                )

                        if 'transcript' in result:
                            with st.expander("View Transcript and Analysis"):
                                st.text_area("Full Transcript", result['transcript'], height=200)
                                if 'important_segments' in result:
                                    st.write("**Important Segments:**")
                                    for segment in result['important_segments']:
                                        st.write(f"- {segment['text']} (Time: {segment['start']:.1f}s - {segment['end']:.1f}s)")
                    else:
                        st.error(f"Error processing video: {result['error']}")

                    os.unlink(temp_path)

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
