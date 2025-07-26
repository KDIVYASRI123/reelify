import React, { useState, useEffect } from 'react';
import { VideoUpload } from '../components/VideoUpload';
import { ProcessingStatus } from '../components/ProcessingStatus';
import { ReelsList } from '../components/ReelsList';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { Video as VideoType } from '../types';
import { Video, Plus, Clock, CheckCircle, AlertCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchVideos();
    }
  }, [user]);

  const fetchVideos = async () => {
    try {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('user_id', user?.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setVideos(data || []);
    } catch (err) {
      console.error('Error fetching videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = (videoId: string) => {
    setSelectedVideo(videoId);
    setShowUpload(false);
    fetchVideos();
  };

  const handleProcessingComplete = () => {
    fetchVideos();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploading':
        return 'Uploading';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Upload videos and create engaging reels with AI-powered analysis.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={() => setShowUpload(true)}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            Upload Video
          </button>
        </div>
      </div>

      {showUpload && (
        <div className="mt-8">
          <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Upload New Video
              </h3>
              <VideoUpload onUploadComplete={handleUploadComplete} />
              <div className="mt-4">
                <button
                  onClick={() => setShowUpload(false)}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedVideo && (
        <div className="mt-8">
          <ProcessingStatus
            videoId={selectedVideo}
            onComplete={handleProcessingComplete}
          />
        </div>
      )}

      <div className="mt-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Your Videos
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Manage your uploaded videos and generated reels.
            </p>
          </div>
          
          {videos.length === 0 ? (
            <div className="text-center py-12">
              <Video className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No videos</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by uploading your first video.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowUpload(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Upload Video
                </button>
              </div>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {videos.map((video) => (
                <li key={video.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Video className="h-8 w-8 text-gray-400 mr-3" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {video.title}
                          </p>
                          <p className="text-sm text-gray-500">
                            Uploaded {new Date(video.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center">
                          {getStatusIcon(video.status)}
                          <span className="ml-2 text-sm text-gray-500">
                            {getStatusText(video.status)}
                          </span>
                        </div>
                        <button
                          onClick={() => setSelectedVideo(video.id)}
                          className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {selectedVideo && (
        <div className="mt-8">
          <ReelsList videoId={selectedVideo} />
        </div>
      )}
    </div>
  ); 
};