import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Play, Pause, Maximize2, Minimize2, RotateCw, Eye } from 'lucide-react';

export interface Hotspot {
  frame_index?: number;
  frame?: number;
  x_coord_pct?: number;
  x_pct?: number;
  x?: number;
  y_coord_pct?: number;
  y_pct?: number;
  y?: number;
  title?: string;
  label?: string;
  description?: string;
}

export interface ThreeSixtyConfig {
  enabled?: boolean;
  frame_count?: number;
  frames: string[];
  rotation_axis?: string;
  reverse_direction?: boolean;
  hotspots?: Hotspot[];
}

export interface ThreeSixtyViewerProps {
  config?: ThreeSixtyConfig;
  frames?: string[];
  hotspots?: Hotspot[];
  productTitle?: string;
}

export const ThreeSixtyViewer: React.FC<ThreeSixtyViewerProps> = ({ 
  config, 
  frames: propFrames, 
  hotspots: propHotspots, 
  productTitle = 'Product' 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const rawFrames = config?.frames || propFrames || [];
  const rawHotspots = config?.hotspots || propHotspots || [];

  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [loadedFrames, setLoadedFrames] = useState<HTMLImageElement[]>([]);
  const [loadProgress, setLoadProgress] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isAutoRotating, setIsAutoRotating] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(null);

  // Dragging & Inertia Physics Refs
  const startXRef = useRef(0);
  const startIndexRef = useRef(0);
  const lastXRef = useRef(0);
  const velocityRef = useRef(0);
  const inertiaAnimRef = useRef<number | null>(null);
  const autoRotateTimerRef = useRef<number | null>(null);

  const totalFrames = rawFrames.length || config?.frame_count || 24;

  // 1. Preload all frames into image buffer
  useEffect(() => {
    let isCancelled = false;
    const images: HTMLImageElement[] = [];
    let loadedCount = 0;

    setLoadProgress(0);
    setIsLoaded(false);

    if (rawFrames.length === 0) return;

    rawFrames.forEach((src, idx) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = src;

      img.onload = () => {
        if (isCancelled) return;
        loadedCount++;
        images[idx] = img;
        setLoadProgress(Math.round((loadedCount / totalFrames) * 100));

        if (loadedCount === totalFrames) {
          setLoadedFrames(images);
          setIsLoaded(true);
        }
      };

      img.onerror = () => {
        if (isCancelled) return;
        loadedCount++;
        setLoadProgress(Math.round((loadedCount / totalFrames) * 100));
        if (loadedCount === totalFrames) {
          setLoadedFrames(images);
          setIsLoaded(true);
        }
      };
    });

    return () => {
      isCancelled = true;
    };
  }, [rawFrames, totalFrames]);

  // 2. Draw current frame onto HTML5 canvas
  const drawFrame = useCallback((frameIdx: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = loadedFrames[frameIdx];
    if (!img) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Scale image maintaining aspect ratio centered on white canvas
    const hRatio = canvas.width / img.width;
    const vRatio = canvas.height / img.height;
    const ratio = Math.min(hRatio, vRatio) * 0.90; // generous padding
    
    const centerShiftX = (canvas.width - img.width * ratio) / 2;
    const centerShiftY = (canvas.height - img.height * ratio) / 2;

    ctx.drawImage(
      img,
      0,
      0,
      img.width,
      img.height,
      centerShiftX,
      centerShiftY,
      img.width * ratio,
      img.height * ratio
    );
  }, [loadedFrames]);

  useEffect(() => {
    if (isLoaded && loadedFrames.length > 0) {
      drawFrame(currentFrameIndex);
    }
  }, [currentFrameIndex, isLoaded, loadedFrames, drawFrame]);

  // 3. Auto-rotation loop
  useEffect(() => {
    if (isAutoRotating && isLoaded && totalFrames > 0) {
      autoRotateTimerRef.current = window.setInterval(() => {
        setCurrentFrameIndex((prev) => (prev + 1) % totalFrames);
      }, 70);
    } else {
      if (autoRotateTimerRef.current) clearInterval(autoRotateTimerRef.current);
    }

    return () => {
      if (autoRotateTimerRef.current) clearInterval(autoRotateTimerRef.current);
    };
  }, [isAutoRotating, isLoaded, totalFrames]);

  // 4. Pointer events for drag scrubbing
  const handlePointerDown = (e: React.PointerEvent) => {
    setIsAutoRotating(false);
    if (inertiaAnimRef.current) {
      cancelAnimationFrame(inertiaAnimRef.current);
      inertiaAnimRef.current = null;
    }

    setIsDragging(true);
    startXRef.current = e.clientX;
    lastXRef.current = e.clientX;
    startIndexRef.current = currentFrameIndex;
    velocityRef.current = 0;

    if (e.currentTarget) {
      (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    }
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging || totalFrames === 0) return;

    const deltaX = e.clientX - startXRef.current;
    velocityRef.current = e.clientX - lastXRef.current;
    lastXRef.current = e.clientX;

    // 12px per frame sensitivity
    const frameShift = Math.floor(deltaX / 12);
    const newIndex = (startIndexRef.current - frameShift) % totalFrames;
    const normalizedIndex = newIndex < 0 ? newIndex + totalFrames : newIndex;

    setCurrentFrameIndex(normalizedIndex);
  };

  const handlePointerUp = () => {
    if (!isDragging) return;
    setIsDragging(false);

    // Inertia physics simulation
    let currentV = velocityRef.current;
    if (Math.abs(currentV) > 1.5) {
      const applyInertia = () => {
        currentV *= 0.92; // Damping
        if (Math.abs(currentV) > 0.3) {
          const shift = currentV > 0 ? -1 : 1;
          setCurrentFrameIndex((prev) => {
            const next = (prev + shift) % totalFrames;
            return next < 0 ? next + totalFrames : next;
          });
          inertiaAnimRef.current = requestAnimationFrame(applyInertia);
        } else {
          inertiaAnimRef.current = null;
        }
      };
      inertiaAnimRef.current = requestAnimationFrame(applyInertia);
    }
  };

  const stepFrame = (delta: number) => {
    setIsAutoRotating(false);
    setCurrentFrameIndex((prev) => {
      const next = (prev + delta) % totalFrames;
      return next < 0 ? next + totalFrames : next;
    });
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
      setIsFullscreen(false);
    }
  };

  // Find hotspots active on current frame
  const currentHotspots = rawHotspots.filter(
    (h) => (h.frame_index ?? h.frame ?? 0) === currentFrameIndex
  );

  const currentDegree = Math.round((currentFrameIndex / totalFrames) * 360);

  return (
    <div
      ref={containerRef}
      className={`relative w-full aspect-square bg-[#ffffff] rounded-[28px] overflow-hidden select-none border border-[#ebebeb]/80 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] ${
        isDragging ? 'cursor-grabbing' : 'cursor-grab'
      }`}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
    >
      {/* Preloader overlay */}
      {!isLoaded && (
        <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-[#ffffff] gap-3">
          <div className="w-10 h-10 border-3 border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin"></div>
          <p className="text-[12px] font-medium tracking-[-0.017em] text-[#787574]">
            Buffering 360° Studio Frames ({loadProgress}%)
          </p>
        </div>
      )}

      {/* Top Floating Badge Bar */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto">
          <span className="px-3 py-1 bg-[#ffffff]/90 backdrop-blur-md rounded-[9999px] text-[11px] font-semibold tracking-[-0.017em] text-[#5433eb] shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 flex items-center gap-1.5">
            <RotateCw size={12} className={isAutoRotating ? 'animate-spin' : ''} />
            360° Interactive Studio
          </span>
          <span className="px-2.5 py-1 bg-[#f2f4f5] rounded-[9999px] text-[11px] font-medium tracking-[-0.017em] text-[#000000]">
            {currentDegree}°
          </span>
        </div>

        <button
          onClick={toggleFullscreen}
          className="p-2 rounded-[9999px] bg-[#ffffff]/90 hover:bg-[#ffffff] text-[#000000] shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 transition-all pointer-events-auto cursor-pointer"
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
        </button>
      </div>

      {/* HTML5 Canvas Rendering */}
      <div className="w-full h-full flex items-center justify-center p-6">
        <canvas
          ref={canvasRef}
          width={800}
          height={800}
          aria-label={`${productTitle} 360 degree interactive view frame ${currentFrameIndex + 1}`}
          className="w-full h-full object-contain pointer-events-none"
        />

        {/* Dynamic Frame-Pinned Hotspots */}
        {isLoaded && currentHotspots.map((hotspot, idx) => {
          const x = hotspot.x_pct ?? hotspot.x_coord_pct ?? hotspot.x ?? 50;
          const y = hotspot.y_pct ?? hotspot.y_coord_pct ?? hotspot.y ?? 50;
          const label = hotspot.label ?? hotspot.title ?? 'Feature Detail';

          return (
            <div
              key={idx}
              style={{ left: `${x}%`, top: `${y}%` }}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 z-30 cursor-pointer pointer-events-auto"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedHotspot(selectedHotspot?.label === label ? null : hotspot);
              }}
            >
              <div className="relative flex items-center">
                <div className="px-3 py-1.5 bg-[#000000]/85 text-[#ffffff] text-[11px] font-medium tracking-[-0.017em] rounded-[9999px] backdrop-blur-md shadow-lg border border-white/20 hover:bg-[#5433eb] transition-all flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-[#ffffff] animate-pulse"></span>
                  {label}
                </div>
              </div>

              {/* Hotspot detail card if clicked */}
              {selectedHotspot && (selectedHotspot.label === label || selectedHotspot.title === label) && (
                <div className="absolute left-1/2 -translate-x-1/2 bottom-8 w-56 p-3 rounded-[20px] bg-[#ffffff] text-[#000000] border border-[#ebebeb] shadow-xl text-xs z-40">
                  <p className="font-semibold text-[#5433eb] text-[12px] mb-1 flex items-center gap-1">
                    <Eye size={12} /> {label}
                  </p>
                  <p className="text-[#787574] text-[11px] leading-relaxed">
                    {hotspot.description || 'Precision engineered hardware component in high-fidelity studio perspective.'}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Floating Center Bottom Scrubber & Controls */}
      <div className="absolute bottom-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-1.5 pointer-events-auto">
          <button
            onClick={() => setIsAutoRotating(!isAutoRotating)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-[9999px] bg-[#ffffff]/95 hover:bg-[#ffffff] text-[#000000] text-[12px] font-medium tracking-[-0.017em] shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 transition-all cursor-pointer"
          >
            {isAutoRotating ? <Pause size={12} className="text-[#5433eb]" /> : <Play size={12} className="text-[#5433eb]" />}
            <span>{isAutoRotating ? 'Pause' : 'Auto Spin'}</span>
          </button>

          <button
            onClick={() => stepFrame(-1)}
            className="w-8 h-8 rounded-[9999px] bg-[#ffffff]/95 hover:bg-[#ffffff] text-[#000000] text-[12px] flex items-center justify-center shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 transition-all cursor-pointer"
            title="Step backward"
          >
            ◀
          </button>
          <button
            onClick={() => stepFrame(1)}
            className="w-8 h-8 rounded-[9999px] bg-[#ffffff]/95 hover:bg-[#ffffff] text-[#000000] text-[12px] flex items-center justify-center shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 transition-all cursor-pointer"
            title="Step forward"
          >
            ▶
          </button>
        </div>

        {/* Drag Scrubber Pill */}
        <div className="px-3 py-1 bg-[#ffffff]/90 rounded-[9999px] text-[11px] font-medium tracking-[-0.017em] text-[#787574] shadow-[0_2px_8px_rgba(0,0,0,0.06)] border border-[#ebebeb]/60 pointer-events-none hidden sm:block">
          Drag horizontally to rotate 360°
        </div>

        {/* Frame indicator */}
        <div className="px-3 py-1 bg-[#f2f4f5] rounded-[9999px] text-[11px] font-semibold tracking-[-0.017em] text-[#000000] pointer-events-auto">
          {currentFrameIndex + 1} / {totalFrames}
        </div>
      </div>
    </div>
  );
};
