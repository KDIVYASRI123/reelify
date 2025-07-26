export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Video {
  id: string;
  user_id: string;
  title: string;
  original_url: string;
  duration: number;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface Transcript {
  id: string;
  video_id: string;
  text: string;
  segments: TranscriptSegment[];
  created_at: string;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  confidence: number;
}

export interface ImportantSegment {
  id: string;
  video_id: string;
  start_time: number;
  end_time: number;
  text: string;
  importance_score: number;
  reason: string;
  created_at: string;
}

export interface Reel {
  id: string;
  video_id: string;
  user_id: string;
  title: string;
  url: string;
  start_time: number;
  end_time: number;
  duration: number;
  status: 'generating' | 'completed' | 'failed';
  created_at: string;
}

export interface ProcessingStatus {
  video_id: string;
  stage: 'upload' | 'audio_extraction' | 'transcription' | 'analysis' | 'reel_generation' | 'completed';
  progress: number;
  message: string;
}