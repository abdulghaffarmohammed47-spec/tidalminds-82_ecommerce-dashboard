import React, { useState } from 'react';
import { ZoomIn, X, ChevronLeft, ChevronRight } from 'lucide-react';

export interface GalleryImage {
  url: string;
  alt?: string;
  is_primary?: boolean;
  width?: number;
  height?: number;
}

interface MediaGalleryProps {
  images: GalleryImage[];
  productTitle: string;
}

export const MediaGallery: React.FC<MediaGalleryProps> = ({ images, productTitle }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  const displayImages = images && images.length > 0
    ? images
    : [{ url: 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=1200&q=80', alt: productTitle, is_primary: true }];

  const currentImage = displayImages[activeIndex] || displayImages[0];

  const handlePrev = (e: React.MouseEvent) => {
    e.stopPropagation();
    setActiveIndex((prev) => (prev === 0 ? displayImages.length - 1 : prev - 1));
    setZoomLevel(1);
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    setActiveIndex((prev) => (prev === displayImages.length - 1 ? 0 : prev + 1));
    setZoomLevel(1);
  };

  return (
    <div className="flex flex-col gap-4 w-full">
      {/* Primary Display Frame with Click-to-Zoom Trigger */}
      <div
        onClick={() => setIsLightboxOpen(true)}
        className="group relative aspect-square w-full bg-[#ffffff] rounded-[28px] border border-[#ebebeb]/80 hover:border-[#5433eb]/40 overflow-hidden flex items-center justify-center p-6 cursor-zoom-in transition-all duration-300 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] hover:shadow-[0_12px_24px_-4px_rgba(0,0,0,0.12)]"
      >
        <img
          src={currentImage.url}
          alt={currentImage.alt || productTitle}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
        />

        {/* Hover Click to Zoom overlay */}
        <div className="absolute bottom-4 right-4 flex items-center gap-1.5 px-3 py-1.5 rounded-[9999px] bg-[#000000]/85 backdrop-blur-md text-[#ffffff] text-[11px] font-medium tracking-[-0.017em] shadow-lg">
          <ZoomIn size={13} className="text-[#c0b5f3]" />
          <span>Click to Zoom</span>
        </div>

        {/* Primary Angle indicator */}
        {currentImage.is_primary && (
          <div className="absolute top-4 left-4 px-3 py-1 rounded-[9999px] bg-[#5433eb] text-[#ffffff] text-[10px] font-semibold tracking-[-0.017em] shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
            Primary View
          </div>
        )}
      </div>

      {/* Responsive Thumbnail Ribbon */}
      {displayImages.length > 1 && (
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
          {displayImages.map((img, idx) => (
            <button
              key={idx}
              onClick={() => setActiveIndex(idx)}
              className={`relative w-20 h-20 rounded-[20px] overflow-hidden bg-[#ffffff] p-1 flex-shrink-0 transition-all cursor-pointer shadow-[0_2px_8px_rgba(0,0,0,0.06)] ${
                activeIndex === idx
                  ? 'border-2 border-[#5433eb] shadow-[0_4px_24px_rgba(69,36,219,0.34)] scale-105'
                  : 'border border-[#ebebeb] opacity-75 hover:opacity-100 hover:border-[#cccccc]'
              }`}
            >
              <img src={img.url} alt="" className="w-full h-full object-cover rounded-[14px]" />
            </button>
          ))}
        </div>
      )}

      {/* Click-to-Zoom Lightbox Modal */}
      {isLightboxOpen && (
        <div
          onClick={() => {
            setIsLightboxOpen(false);
            setZoomLevel(1);
          }}
          className="fixed inset-0 z-50 bg-[#000000]/95 backdrop-blur-xl flex flex-col items-center justify-between p-4 sm:p-8 animate-in fade-in duration-200 select-none"
        >
          {/* Lightbox Header */}
          <div className="w-full max-w-6xl flex items-center justify-between text-[#ffffff] z-10">
            <div>
              <p className="text-[14px] font-semibold tracking-[-0.014em]">{productTitle}</p>
              <p className="text-[11px] text-[#acb0aa] tracking-[-0.017em]">
                Image {activeIndex + 1} of {displayImages.length}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setZoomLevel((prev) => (prev === 1 ? 2 : 1));
                }}
                className="px-3 py-1.5 rounded-[9999px] bg-white/10 hover:bg-white/20 text-xs font-medium text-white transition-all flex items-center gap-1 cursor-pointer"
              >
                <ZoomIn size={13} />
                <span>{zoomLevel === 1 ? 'Zoom 2x' : 'Reset'}</span>
              </button>
              <button
                onClick={() => setIsLightboxOpen(false)}
                className="p-2 rounded-[9999px] bg-white/10 hover:bg-white/20 text-white transition-all cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Lightbox Main Stage */}
          <div
            className="relative flex-1 w-full max-w-5xl flex items-center justify-center overflow-hidden my-4"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={currentImage.url}
              alt={currentImage.alt || productTitle}
              style={{ transform: `scale(${zoomLevel})` }}
              className="max-h-[80vh] max-w-full object-contain transition-transform duration-300 cursor-pointer"
              onClick={() => setZoomLevel((prev) => (prev === 1 ? 2 : 1))}
            />

            {/* Navigation Arrows */}
            {displayImages.length > 1 && (
              <>
                <button
                  onClick={handlePrev}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-11 h-11 rounded-[9999px] bg-black/60 hover:bg-black/90 text-white flex items-center justify-center border border-white/20 transition-all cursor-pointer"
                >
                  <ChevronLeft size={22} />
                </button>
                <button
                  onClick={handleNext}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-11 h-11 rounded-[9999px] bg-black/60 hover:bg-black/90 text-white flex items-center justify-center border border-white/20 transition-all cursor-pointer"
                >
                  <ChevronRight size={22} />
                </button>
              </>
            )}
          </div>

          {/* Bottom Thumbnails */}
          {displayImages.length > 1 && (
            <div
              className="flex gap-2.5 overflow-x-auto p-2 rounded-[9999px] bg-white/10 backdrop-blur-md max-w-xl"
              onClick={(e) => e.stopPropagation()}
            >
              {displayImages.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setActiveIndex(idx);
                    setZoomLevel(1);
                  }}
                  className={`relative w-12 h-12 rounded-[14px] overflow-hidden transition-all flex-shrink-0 cursor-pointer ${
                    activeIndex === idx ? 'ring-2 ring-[#5433eb] scale-110' : 'opacity-60 hover:opacity-100'
                  }`}
                >
                  <img src={img.url} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
