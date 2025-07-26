import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { ProcessingStatus as ProcessingStatusType } from '../types';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface ProcessingStatusProps {
  videoId: string;
  onComplete: () => void;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ videoId, onComplete }) => {
  const [status, setStatus] = useState<ProcessingStatusType | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const { data, error } = await supabase
          .from('processing_status')
          .select('*')
          .eq('video_id', videoId)
          .single();

        if (error && error.code !== 'PGRST116') {
          throw error;
        }

        if (data) {
          setStatus(data);
          if (data.stage === 'completed') {
            onComplete();
          }
        }
      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchStatus();

    // Subscribe to real-time updates
    const subscription = supabase
      .channel(`processing_status_${videoId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'processing_status',
          filter: `video_id=eq.${videoId}`
        },
        (payload) => {
          const newStatus = payload.new as ProcessingStatusType;
          setStatus(newStatus);
          if (newStatus.stage === 'completed') {
            onComplete();
          }
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [videoId, onComplete]);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <p className="text-sm text-red-800">Error loading processing status: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div className="flex items-center">
          <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
          <div className="ml-3">
            <p className="text-sm text-blue-800">Initializing processing...</p>
          </div>
        </div>
      </div>
    );
  }

  const stages = [
    { key: 'upload', label: 'Upload Complete' },
    { key: 'audio_extraction', label: 'Extracting Audio' },
    { key: 'transcription', label: 'Converting Speech to Text' },
    { key: 'analysis', label: 'Analyzing Content' },
    { key: 'reel_generation', label: 'Generating Reels' },
    { key: 'completed', label: 'Processing Complete' }
  ];

  const currentStageIndex = stages.findIndex(stage => stage.key === status.stage);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Processing Video</h3>
        <p className="text-sm text-gray-600">{status.message}</p>
      </div>

      <div className="space-y-3">
        {stages.map((stage, index) => {
          const isCompleted = index < currentStageIndex;
          const isCurrent = index === currentStageIndex;
          const isPending = index > currentStageIndex;

          return (
            <div key={stage.key} className="flex items-center">
              <div className="flex-shrink-0">
                {isCompleted ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : isCurrent ? (
                  <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
                ) : (
                  <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
                )}
              </div>
              <div className="ml-3">
                <p className={`text-sm font-medium ${
                  isCompleted ? 'text-green-700' :
                  isCurrent ? 'text-blue-700' :
                  'text-gray-500'
                }`}>
                  {stage.label}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4">
        <div className="bg-gray-200 rounded-full h-2">
          <div
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${status.progress}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">{status.progress}% complete</p>
      </div>
    </div>
  );
};