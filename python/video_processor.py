import subprocess
import whisper
import openai
import os
import tempfile
import json
from typing import List, Dict, Any


class VideoProcessor:
    def __init__(self):
        # Load Whisper model
        self.whisper_model = whisper.load_model("base")

        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    def process_video(self, video_path: str, reel_count: int = 2, reel_duration: int = 30) -> Dict[str, Any]:
        try:
            # Step 1: Extract audio from video
            audio_path = self.extract_audio(video_path)

            # Step 2: Transcribe audio with Whisper
            transcript_result = self.audio_to_text(audio_path)

            # Step 3: Use AI to pick important segments
            important_segments = self.analyze_text_segments(
                transcript_result['text'],
                transcript_result['segments'],
                reel_count
            )

            # Step 4: Generate video clips
            reels = self.create_reels(video_path, important_segments, reel_duration)

            # Clean up temp audio
            os.unlink(audio_path)

            return {
                'success': True,
                'reels': reels,
                'transcript': transcript_result['text'],
                'important_segments': important_segments
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def extract_audio(self, video_path: str) -> str:
        """
        Extract mono 16kHz PCM audio from video using ffmpeg.
        """
        audio_path = tempfile.mktemp(suffix='.wav')
        try:
            subprocess.run([
                "ffmpeg",
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                audio_path
            ], check=True, capture_output=True)
            return audio_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error extracting audio: {e.stderr.decode()}")

    def audio_to_text(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper.
        """
        try:
            result = self.whisper_model.transcribe(audio_path)
            return {
                'text': result['text'],
                'segments': result['segments']
            }
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    def analyze_text_segments(self, full_text: str, segments: List[Dict], reel_count: int) -> List[Dict]:
        """
        Ask OpenAI to pick the most important segments for reels.
        """
        try:
            segment_texts = [
                {
                    'index': i,
                    'text': seg['text'].strip(),
                    'start': seg['start'],
                    'end': seg['end']
                }
                for i, seg in enumerate(segments)
            ]

            prompt = f"""
            Analyze the following video transcript and identify the {reel_count} most important, engaging, and meaningful segments that would make great short video reels.

            Consider segments that are:
            - Most engaging or entertaining
            - Contain key information or insights
            - Have emotional impact
            - Are self-contained and make sense on their own

            Full transcript: {full_text}

            Segments with timestamps:
            {json.dumps(segment_texts, indent=2)}

            Return the indices of the {reel_count} most important segments as a JSON array of numbers.
            Example: [2, 7, 15]
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert video editor who selects impactful clips for reels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )

            important_indices = json.loads(response.choices[0].message.content.strip())

            important_segments = []
            for idx in important_indices:
                if 0 <= idx < len(segment_texts):
                    segment = segment_texts[idx]
                    important_segments.append({
                        'text': segment['text'],
                        'start': segment['start'],
                        'end': segment['end']
                    })

            return important_segments

        except Exception as e:
            # Fallback: evenly pick from start
            fallback = []
            step = max(1, len(segments) // reel_count)
            for i in range(0, len(segments), step):
                segment = segments[i]
                fallback.append({
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end']
                })
                if len(fallback) >= reel_count:
                    break
            return fallback

    def create_reels(self, video_path: str, important_segments: List[Dict], reel_duration: int) -> List[str]:
        """
        Generate reel video clips using ffmpeg from the selected segments.
        """
        reels = []

        for i, segment in enumerate(important_segments):
            try:
                start_time = max(0, segment['start'] - 2)
                end_time = min(start_time + reel_duration, segment['end'] + 2)
                output_path = tempfile.mktemp(suffix=f'_reel_{i+1}.mp4')

                subprocess.run([
                    "ffmpeg",
                    "-ss", str(start_time),
                    "-i", video_path,
                    "-t", str(end_time - start_time),
                    "-vcodec", "libx264",
                    "-acodec", "aac",
                    "-crf", "23",
                    "-preset", "medium",
                    output_path
                ], check=True, capture_output=True)

                reels.append(output_path)
            except subprocess.CalledProcessError as e:
                print(f"Error creating reel {i+1}: {e.stderr.decode()}")
                continue

        return reels
