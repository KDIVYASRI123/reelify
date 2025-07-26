import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { Reel } from '../types';
import { Play, Download, Share2, Clock, Calendar } from 'lucide-react';

interface ReelsListProps {
  videoId: string;
}

export const ReelsList: React.FC<ReelsListProps> = ({ videoId }) => {
  const [reels, setReels] = useState<Reel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReels = async () => {
      try {
        const { data, error } = await supabase
          .from('reels')
          .select('*')
          .eq('video_id', videoId)
          .order('created_at', { ascending: false });

        if (error) throw error;
        setReels(data || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchReels();

    // Subscribe to real-time updates
    const subscription = supabase
      .channel(`reels_${videoId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'reels',
          filter: `video_id=eq.${videoId}`
        },
        () => {
          fetchReels();
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [videoId]);

  const formatDuration = (seconds: number) => {
    return `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-sm text-red-800">Error loading reels: {error}</p>
      </div>
    );
  }

  if (reels.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No reels generated yet. Processing may still be in progress.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">Generated Reels</h3>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {reels.map((reel) => (
          <div key={reel.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
            <div className="aspect-video bg-gray-100 relative">
              {reel.status === 'completed' ? (
                <video
                  src={reel.url}
                  className="w-full h-full object-cover"
                  poster={`${reel.url}#t=1`}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
              )}
              
              <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                <Play className="h-12 w-12 text-white opacity-0 hover:opacity-100 transition-opacity" />
              </div>
            </div>
            
            <div className="p-4">
              <h4 className="font-medium text-gray-900 mb-2 truncate">{reel.title}</h4>
              
              <div className="flex items-center text-sm text-gray-500 space-x-4 mb-3">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  {formatDuration(reel.duration)}
                </div>
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {formatDate(reel.created_at)}
                </div>
              </div>
              
              {reel.status === 'completed' ? (
                <div className="flex space-x-2">
                  <button
                    onClick={() => window.open(reel.url, '_blank')}
                    className="flex-1 bg-indigo-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Play
                  </button>
                  <button
                    onClick={() => {
                      const a = document.createElement('a');
                      a.href = reel.url;
                      a.download = `${reel.title}.mp4`;
                      a.click();
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (navigator.share) {
                        navigator.share({
                          title: reel.title,
                          url: reel.url
                        });
                      } else {
                        navigator.clipboard.writeText(reel.url);
                      }
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <Share2 className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-2">
                  <p className="text-sm text-yellow-800">
                    {reel.status === 'generating' ? 'Generating reel...' : 'Processing failed'}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};