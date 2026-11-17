import React, { useRef } from 'react';

interface Props {
  videoUrl: string;
  posterUrl: string;
  chapters: { time_sec: number; title: string }[];
}

export const ProductVideoPlayer: React.FC<Props> = ({ videoUrl, posterUrl, chapters }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  const seekTo = (sec: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = sec;
      videoRef.current.play();
    }
  };

  return (
    <div className="w-full bg-[#ffffff] rounded-[28px] overflow-hidden shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] p-3">
      <video 
        ref={videoRef}
        src={videoUrl}
        poster={posterUrl}
        controls
        className="w-full aspect-video rounded-[20px] object-cover bg-[#000000]"
      />
      {chapters.length > 0 && (
        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          {chapters.map((chap, idx) => (
            <button
              key={idx}
              onClick={() => seekTo(chap.time_sec)}
              className="px-3 py-1.5 rounded-[9999px] bg-[#f2f4f5] hover:bg-[#ebebeb] text-[#000000] text-[12px] font-['GT_Standard'] tracking-[-0.017em] whitespace-nowrap transition-colors"
            >
              {chap.title}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
