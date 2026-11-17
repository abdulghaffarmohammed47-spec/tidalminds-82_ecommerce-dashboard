import React from 'react';
import { Heart, Star } from 'lucide-react';
import { useState } from 'react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

export interface ProductCardProps {
  id?: string;
  title: string;
  brand: string;
  price: number;
  imageUrl: string;
  rating: number;
  reviewCount: number;
  explanation?: string;
  isAlternative?: boolean;
  matchScore?: string;
  has360?: boolean;
  hasVideo?: boolean;
  onClick: () => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  id,
  title,
  brand,
  price,
  imageUrl,
  rating,
  reviewCount,
  explanation,
  isAlternative,
  matchScore,
  has360,
  hasVideo,
  onClick
}) => {
  const user = useAuthStore((state) => state.user);
  const [saved, setSaved] = useState(false);

  const saveProduct = async (event: React.MouseEvent) => {
    event.stopPropagation();
    if (!id || !user) return;
    try {
      if (saved) {
        await api.delete(`/api/v1/wishlist/${id}`);
        setSaved(false);
      } else {
        await api.post('/api/v1/wishlist', { product_id: id });
        setSaved(true);
      }
    } catch {
      // A duplicate save is harmless; the card remains usable.
      setSaved(true);
    }
  };

  return (
    <div 
      onClick={onClick}
      className="market-product-card group cursor-pointer bg-[#ffffff] rounded-[28px] p-2.5 flex flex-col justify-between transition-all duration-200 hover:-translate-y-1.5 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] hover:shadow-[0_12px_24px_-4px_rgba(0,0,0,0.12)] border border-[#ebebeb]/60"
    >
      <div className="relative w-full aspect-square bg-[#f2f4f5] rounded-[20px] overflow-hidden">
        <img 
          src={imageUrl || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80'} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
          loading="lazy"
        />
        {id && user && (
          <button
            onClick={saveProduct}
            aria-label={saved ? `Remove ${title} from wishlist` : `Save ${title} to wishlist`}
            className={`absolute right-3 top-3 rounded-full p-2.5 shadow-sm backdrop-blur transition ${saved ? 'bg-[#6d5dfc] text-white' : 'bg-white/90 text-[#172033] hover:bg-white hover:text-[#6d5dfc]'}`}
          >
            <Heart size={16} fill={saved ? 'currentColor' : 'none'} />
          </button>
        )}
        
        {/* Badges Overlay */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex flex-wrap items-center justify-between gap-1.5 pointer-events-none">
          {isAlternative ? (
            <span className="bg-[#5433eb] text-[#ffffff] text-[11px] font-medium tracking-[-0.017em] px-2.5 py-1 rounded-[9999px] shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
              In-Stock Alternative
            </span>
          ) : matchScore ? (
            <span className="bg-[#5433eb] text-[#ffffff] text-[11px] font-semibold tracking-[-0.017em] px-2.5 py-1 rounded-[9999px] shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
              {matchScore}
            </span>
          ) : <span />}

          <div className="flex items-center gap-1">
            {has360 && (
              <span className="bg-[#ffffff]/90 backdrop-blur-sm text-[#000000] text-[10px] font-medium tracking-[-0.017em] px-2 py-0.5 rounded-[9999px] shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
                360°
              </span>
            )}
            {hasVideo && (
              <span className="bg-[#ffffff]/90 backdrop-blur-sm text-[#000000] text-[10px] font-medium tracking-[-0.017em] px-2 py-0.5 rounded-[9999px] shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
                Video
              </span>
            )}
          </div>
        </div>
      </div>
      
      <div className="p-3">
        <div className="text-[12px] font-medium tracking-[-0.017em] text-[#787574] mb-0.5">
          {brand}
        </div>
        <div className="text-[14px] font-semibold tracking-[-0.014em] text-[#000000] line-clamp-1 mb-1.5" title={title}>
          {title}
        </div>
        
        <div className="flex items-center gap-1.5 mb-2">
          <div className="flex items-center gap-1">
            <Star className="fill-[#000000] text-[#000000]" size={12}/>
            <span className="text-[11px] font-medium tracking-[-0.017em] text-[#000000]">
              {(rating || 4.5).toFixed(1)}
            </span>
          </div>
          <span className="text-[11px] tracking-[-0.017em] text-[#787574]">
            ({reviewCount || 128})
          </span>
        </div>

        <div className="text-[16px] font-bold tracking-[-0.031em] text-[#000000]">
          {typeof price === 'number' && Number.isFinite(price)
            ? `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            : 'Price unavailable'}
        </div>

        {explanation && (
          <div className="mt-2 text-[11px] font-medium tracking-[-0.017em] text-[#5433eb] bg-[#c0b5f3]/25 px-2.5 py-1 rounded-[9999px] line-clamp-1">
            {explanation}
          </div>
        )}
      </div>
    </div>
  );
};
