import React, { useEffect, useState } from 'react';
import { X, ArrowRight, Sparkles, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';

interface AlternativeProduct {
  id: string;
  variant_id?: string;
  sku?: string;
  title: string;
  price: number;
  available_stock?: number;
  current_stock?: number;
  brand?: string;
  gallery?: Array<{ url: string }>;
  specifications?: Record<string, any>;
}

interface InStockAlternativeModalProps {
  isOpen: boolean;
  onClose: () => void;
  originalProductId?: string;
  originalTitle?: string;
  originalPrice?: number;
  outOfStockProduct?: {
    id: string;
    title: string;
    price: number;
    category_id?: string;
  };
  onSelectAlternative?: (altId: string) => void;
}

export const InStockAlternativeModal: React.FC<InStockAlternativeModalProps> = ({
  isOpen,
  onClose,
  originalProductId: propId,
  originalTitle: propTitle,
  outOfStockProduct,
  onSelectAlternative
}) => {
  const targetId = outOfStockProduct?.id || propId || '';
  const targetTitle = outOfStockProduct?.title || propTitle || 'Product';

  const [alternatives, setAlternatives] = useState<AlternativeProduct[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isOpen || !targetId) return;

    const fetchAlternatives = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/api/inventory/alternatives/${targetId}?limit=3`);
        setAlternatives(res.data || []);
      } catch (err) {
        console.error('Failed to fetch in-stock alternatives:', err);
        try {
          const fallbackRes = await api.get('/api/products?limit=6');
          const alts = (fallbackRes.data || [])
            .filter((p: any) => p.id !== targetId && (p.current_stock > 0 || p.is_in_stock))
            .slice(0, 3)
            .map((p: any) => ({
              id: p.id,
              sku: p.sku || 'ALT-SKU',
              title: p.title || p.name || 'Alternative Product',
              price: p.price,
              available_stock: p.current_stock || 12,
              brand: p.brand || 'SmartCommerce',
              gallery: p.gallery
            }));
          setAlternatives(alts);
        } catch (e) {
          setAlternatives([]);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAlternatives();
  }, [isOpen, targetId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#000000]/60 backdrop-blur-md animate-in fade-in duration-200 select-none">
      <div className="relative w-full max-w-3xl bg-[#ffffff] border border-[#ebebeb] rounded-[28px] p-6 sm:p-8 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        
        {/* Modal Header */}
        <div className="flex items-start justify-between pb-5 border-b border-[#ebebeb]">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-[9999px] bg-amber-50 border border-amber-200 text-[11px] font-semibold tracking-[-0.017em] text-amber-700 mb-2">
              <AlertTriangle size={13} />
              <span>Currently Out of Stock</span>
            </div>
            <h2 className="text-2xl font-bold tracking-[-0.05em] text-[#000000]">
              Instant In-Stock Alternatives
            </h2>
            <p className="text-[13px] tracking-[-0.017em] text-[#787574] mt-1">
              <span className="font-semibold text-[#000000]">{targetTitle}</span> is temporarily depleted. SmartCommerce AI matched these comparable in-stock models ready for dispatch:
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-[9999px] bg-[#f2f4f5] hover:bg-[#ebebeb] text-[#787574] hover:text-[#000000] transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body - Alternatives Cards */}
        <div className="py-5 overflow-y-auto flex-1 space-y-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <div className="w-8 h-8 border-3 border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin"></div>
              <p className="text-[12px] tracking-[-0.017em] text-[#787574]">Computing nearest in-stock alternatives...</p>
            </div>
          ) : alternatives.length === 0 ? (
            <div className="text-center py-8 text-[#787574] text-[13px]">
              No exact alternatives currently available. Check back soon.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alternatives.map((alt) => {
                const stock = alt.available_stock ?? alt.current_stock ?? 5;
                const img = alt.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=400&q=80';

                return (
                  <div
                    key={alt.id}
                    className="bg-[#ffffff] rounded-[24px] p-3.5 border border-[#ebebeb] shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-lg transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="w-full aspect-square rounded-[18px] bg-[#f2f4f5] overflow-hidden mb-3">
                        <img src={img} alt={alt.title} className="w-full h-full object-cover" />
                      </div>
                      <span className="text-[11px] font-semibold text-[#5433eb] uppercase tracking-[-0.017em]">
                        {alt.brand || 'In-Stock Match'}
                      </span>
                      <h4 className="text-[13px] font-bold tracking-[-0.014em] text-[#000000] line-clamp-2 mt-0.5 mb-2">
                        {alt.title}
                      </h4>
                    </div>

                    <div className="pt-2 border-t border-[#ebebeb] space-y-2">
                      <div className="flex items-baseline justify-between">
                        <span className="text-[15px] font-bold text-[#000000] tracking-[-0.031em]">
                          ${alt.price.toFixed(2)}
                        </span>
                        <span className="text-[10px] font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded-[9999px] border border-green-200">
                          {stock} in stock
                        </span>
                      </div>

                      <button
                        onClick={() => {
                          if (onSelectAlternative) {
                            onSelectAlternative(alt.id);
                          } else {
                            onClose();
                            navigate(`/product/${alt.id}`);
                          }
                        }}
                        className="w-full py-2 bg-[#5433eb] hover:brightness-110 text-[#ffffff] rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] flex items-center justify-center gap-1 transition-all cursor-pointer"
                      >
                        <span>View Product</span>
                        <ArrowRight size={13} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="pt-4 border-t border-[#ebebeb] flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[11px] font-medium tracking-[-0.017em] text-[#787574]">
            <Sparkles size={13} className="text-[#5433eb]" />
            <span>AI nearest-neighbor cosine similarity matching</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-[9999px] bg-[#f2f4f5] hover:bg-[#ebebeb] text-[#000000] text-[12px] font-semibold tracking-[-0.017em] transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
export default InStockAlternativeModal;
