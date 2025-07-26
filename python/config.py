import os
from pathlib import Path

# Application settings
APP_NAME = "Video to Reels Converter"
VERSION = "1.0.0"

# File settings
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
TEMP_DIR = Path("temp")
OUTPUT_DIR = Path("output")

# Create directories if they don't exist
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large

# Video processing settings
DEFAULT_REEL_DURATION = 30  # seconds
MAX_REEL_COUNT = 5
MIN_REEL_DURATION = 15
MAX_REEL_DURATION = 60

# Database settings
DATABASE_PATH = "app_database.db"

# FFmpeg settings
FFMPEG_AUDIO_CODEC = "pcm_s16le"
FFMPEG_AUDIO_CHANNELS = 1
FFMPEG_AUDIO_RATE = "16000"
FFMPEG_VIDEO_CODEC = "libx264"
FFMPEG_VIDEO_CRF = "23"
FFMPEG_VIDEO_PRESET = "medium"
