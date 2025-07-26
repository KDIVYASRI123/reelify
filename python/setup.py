#!/usr/bin/env python3
"""
Setup script for Video to Reels Converter
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found")
        return False

def install_requirements():
    """Install Python requirements"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Python requirements installed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = ["temp", "output", "uploads"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Directories created")

def setup_database():
    """Initialize the database"""
    try:
        from database import init_database
        init_database()
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Setting up Video to Reels Converter...")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("\nFFmpeg installation required:")
        print("- Windows: Download from https://ffmpeg.org/download.html")
        print("- macOS: brew install ffmpeg")
        print("- Ubuntu/Debian: sudo apt install ffmpeg")
        print("- CentOS/RHEL: sudo yum install ffmpeg")
        
        response = input("\nContinue setup without FFmpeg? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("2. Run: streamlit run app.py")
    print("\nNote: Make sure FFmpeg is installed for video processing.")

if __name__ == "__main__":
    main()
