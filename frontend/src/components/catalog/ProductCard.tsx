import React from 'react';
import { Star } from 'lucide-react';

interface Props {
  title: string;
  brand: string;
  price: number;
  imageUrl: string;
  rating: number;
  reviewCount: number;
  explanation?: string;
  isAlternative?: boolean;
  onClick: () => void;
}

export const ProductCard: React.FC<Props> = ({
  title, brand, price, imageUrl, rating, reviewCount, explanation, isAlternative, onClick
}) => {
  return (
    <div 
      onClick={onClick}
      className="group cursor-pointer bg-[#ffffff] rounded-[28px] p-2 flex flex-col justify-between transition-transform duration-200 hover:-translate-y-1 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)]"
    >
      <div className="relative w-full aspect-square bg-[#f2f4f5] rounded-[20px] overflow-hidden">
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
        />
        {isAlternative && (
          <span className="absolute top-3 left-3 bg-[#5433eb] text-[#ffffff] text-[11px] font-['GT_Standard'] tracking-[-0.017em] px-2.5 py-1 rounded-[9999px] shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
            In-Stock Alternative
          </span>
        )}
      </div>
      
      <div className="p-3">
        <div className="text-[12px] font-['GT_Standard'] tracking-[-0.017em] text-[#787574] mb-0.5">
          {brand}
        </div>
        <div className="text-[14px] font-['GT_Standard'] tracking-[-0.014em] text-[#000000] font-medium line-clamp-1 mb-1.5">
          {title}
        </div>
        
        <div className="flex items-center gap-1 mb-2">
          <Star className="fill-[#000000] text-[#000000]" size={12}/>
          <span className="text-[11px] font-['GT_Standard'] tracking-[-0.017em] text-[#000000]">
            {rating.toFixed(1)}
          </span>
          <span className="text-[11px] font-['GT_Standard'] tracking-[-0.017em] text-[#787574]">
            ({reviewCount})
          </span>
        </div>

        <div className="text-[16px] font-['GT_Standard'] tracking-[-0.031em] text-[#000000] font-semibold">
          ₹{price.toLocaleString('en-IN')}
        </div>

        {explanation && (
          <div className="mt-2 text-[11px] font-['GT_Standard'] tracking-[-0.017em] text-[#5433eb] bg-[#c0b5f3]/20 px-2 py-1 rounded-[9999px] line-clamp-1">
            {explanation}
          </div>
        )}
      </div>
    </div>
  );
};
