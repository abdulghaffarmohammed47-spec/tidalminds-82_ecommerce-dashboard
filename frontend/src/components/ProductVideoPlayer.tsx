import React, { useRef, useState } from 'react';
import { Sparkles, Clock } from 'lucide-react';

export interface VideoChapter {
  time_sec?: number;
  timestamp_sec?: number;
  time?: number;
  title: string;
  description?: string;
}

export interface VideoShowcaseConfig {
  enabled?: boolean;
  video_url?: string;
  videoUrl?: string;
  poster_url?: string;
  posterUrl?: string;
  duration_sec?: number;
  title?: string;
  chapters?: VideoChapter[];
}

export interface ProductVideoPlayerProps {
  config?: VideoShowcaseConfig;
  videoUrl?: string;
  posterUrl?: string;
  chapters?: VideoChapter[];
  title?: string;
}

export const ProductVideoPlayer: React.FC<ProductVideoPlayerProps> = ({ 
  config, 
  videoUrl: propVideoUrl, 
  posterUrl: propPosterUrl, 
  chapters: propChapters,
  title: propTitle
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [, setIsPlaying] = useState(false);
  const [activeChapterIndex, setActiveChapterIndex] = useState(0);

  const videoUrl = propVideoUrl || config?.video_url || config?.videoUrl || 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4';
  const posterUrl = propPosterUrl || config?.poster_url || config?.posterUrl || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=1200&q=80';
  const chapters = propChapters || config?.chapters || [];
  const videoTitle = propTitle || config?.title || 'Industrial Design & Product Showcase';

  const seekTo = (sec: number, idx: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = sec;
      videoRef.current.play();
      setIsPlaying(true);
      setActiveChapterIndex(idx);
    }
  };

  return (
    <div className="w-full bg-[#ffffff] rounded-[28px] overflow-hidden shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] p-3.5 border border-[#ebebeb]/80">
      <div className="relative w-full aspect-video rounded-[20px] overflow-hidden bg-[#000000]">
        <video 
          ref={videoRef}
          src={videoUrl}
          poster={posterUrl}
          controls
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          className="w-full h-full object-cover"
        />

        {/* Floating title tag */}
        <div className="absolute top-3 left-3 bg-[#000000]/75 backdrop-blur-md text-[#ffffff] text-[11px] font-medium tracking-[-0.017em] px-3 py-1 rounded-[9999px] border border-white/10 pointer-events-none hidden sm:flex items-center gap-1.5">
          <Sparkles size={12} className="text-[#c0b5f3]" />
          {videoTitle}
        </div>
      </div>

      {/* Interactive Chapter Scrubbing Timeline */}
      {chapters.length > 0 && (
        <div className="mt-3.5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[12px] font-semibold tracking-[-0.017em] text-[#000000] flex items-center gap-1.5">
              <Clock size={13} className="text-[#5433eb]" />
              Interactive Chapter Navigation
            </span>
            <span className="text-[11px] tracking-[-0.017em] text-[#787574]">
              Click to jump timestamp
            </span>
          </div>

          <div className="flex gap-2 overflow-x-auto pb-1.5 scrollbar-none">
            {chapters.map((chap, idx) => {
              const timeSec = chap.time_sec ?? chap.timestamp_sec ?? chap.time ?? 0;
              const isActive = activeChapterIndex === idx;

              return (
                <button
                  key={idx}
                  onClick={() => seekTo(timeSec, idx)}
                  className={`px-3.5 py-1.5 rounded-[9999px] text-[12px] font-medium tracking-[-0.017em] whitespace-nowrap transition-all cursor-pointer flex items-center gap-1.5 ${
                    isActive 
                      ? 'bg-[#5433eb] text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)]' 
                      : 'bg-[#f2f4f5] hover:bg-[#ebebeb] text-[#000000]'
                  }`}
                >
                  <span className={`text-[10px] ${isActive ? 'text-[#ffffff]/80' : 'text-[#787574]'}`}>
                    {Math.floor(timeSec / 60)}:{String(timeSec % 60).padStart(2, '0')}
                  </span>
                  <span>{chap.title}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
