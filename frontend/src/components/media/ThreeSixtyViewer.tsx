import React, { useRef, useState } from 'react';

interface Props {
  frames: string[];
  hotspots?: { frame_index: number; x_pct: number; y_pct: number; label: string }[];
}

export const ThreeSixtyViewer: React.FC<Props> = ({ frames, hotspots = [] }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const startXRef = useRef(0);
  const startIndexRef = useRef(0);

  const handlePointerDown = (e: React.PointerEvent) => {
    setIsDragging(true);
    startXRef.current = e.clientX;
    startIndexRef.current = currentIndex;
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging || frames.length === 0) return;
    const deltaX = e.clientX - startXRef.current;
    const frameShift = Math.floor(deltaX / 12);
    const newIndex = (startIndexRef.current - frameShift) % frames.length;
    setCurrentIndex(newIndex < 0 ? newIndex + frames.length : newIndex);
  };

  const handlePointerUp = () => setIsDragging(false);

  const activeHotspot = hotspots.find(h => h.frame_index === currentIndex);

  return (
    <div 
      className="relative w-full aspect-square bg-[#ffffff] rounded-[28px] overflow-hidden select-none cursor-grab active:cursor-grabbing shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)]"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
    >
      <img 
        src={frames[currentIndex]} 
        alt={`360 Frame ${currentIndex + 1}`}
        className="w-full h-full object-contain p-4 pointer-events-none"
      />
      {activeHotspot && (
        <div 
          className="absolute transform -translate-x-1/2 -translate-y-1/2 px-3 py-1.5 bg-[#000000]/80 text-[#ffffff] text-[11px] font-['GT_Standard'] tracking-[-0.017em] rounded-[9999px] backdrop-blur-md transition-all duration-150"
          style={{ left: `${activeHotspot.x_pct}%`, top: `${activeHotspot.y_pct}%` }}
        >
          {activeHotspot.label}
        </div>
      )}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-3 py-1 bg-[#ffffff]/90 rounded-[9999px] text-[11px] font-['GT_Standard'] tracking-[-0.017em] text-[#787574] shadow-[0_2px_8px_rgba(0,0,0,0.06)] pointer-events-none">
        Drag to rotate 360°
      </div>
    </div>
  );
};
