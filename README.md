# reelify
Reelify – Project Documentation
Overview
Reelify is an AI-powered video processing application that converts long videos into engaging short-form reels.
The system allows users to:

Upload videos

Extract audio

Transcribe using OpenAI Whisper

Generate AI-selected short segments

Export reels optimized for social media

Features
User Authentication

Firebase / Supabase authentication

Secure login and signup

Video Upload

Drag-and-drop video uploads

Client-side validation for video size and format

Processing Pipeline

Audio Extraction: Using FFmpeg

Transcription: Whisper/OpenAI for speech-to-text

Segment Generation: AI determines highlights

Reel Creation: Generates 15–30s reels

Preview & Metadata

Video preview

Displays resolution, duration, FPS, size

Export & Download

Download reels as MP4

Transcription file as .txt

Tech Stack
Frontend
React + TypeScript + Vite

TailwindCSS + ShadCN UI

Firebase for Auth

Lucide-react icons

Backend
Node.js + Express (or Streamlit for Python version)

FFmpeg for video/audio processing

Whisper (OpenAI) for transcription

Python (for AI-heavy tasks)

Storage
Firebase Cloud Storage (or local uploads for dev)

