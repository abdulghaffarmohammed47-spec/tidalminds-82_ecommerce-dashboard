import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ShoppingCart, ArrowLeft, Cpu, RotateCw, PlaySquare, Image as ImageIcon, CheckCircle2, AlertCircle, Sparkles, Star } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';
import { ThreeSixtyViewer, type ThreeSixtyConfig } from '../components/ThreeSixtyViewer';
import { ProductVideoPlayer, type VideoShowcaseConfig } from '../components/ProductVideoPlayer';
import { MediaGallery } from '../components/MediaGallery';
import { InStockAlternativeModal } from '../components/InStockAlternativeModal';
import { ProductCard } from '../components/ProductCard';

interface Product {
  id: string;
  sku?: string;
  name?: string;
  title: string;
  brand?: string;
  description?: string;
  price?: number;
  compare_at_price?: number;
  current_stock: number;
  is_in_stock?: boolean;
  rating_avg?: number;
  review_count?: number;
  specifications: Record<string, any>;
  gallery?: Array<{ url: string; alt?: string; is_primary?: boolean }>;
  view_360?: ThreeSixtyConfig;
  video_showcase?: VideoShowcaseConfig;
  variants?: Array<{ id: string; sku: string; name?: string }>;
}

export const ProductDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [similarProducts, setSimilarProducts] = useState<any[]>([]);
  const [activeMediaTab, setActiveMediaTab] = useState<'360' | 'video' | 'gallery'>('gallery');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [addingToCart, setAddingToCart] = useState(false);
  const [isAlternativeModalOpen, setIsAlternativeModalOpen] = useState(false);
  const [cartSuccessMessage, setCartSuccessMessage] = useState('');

  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    const fetchProduct = async () => {
      setIsLoading(true);
      setError('');
      try {
        const response = await api.get(`/api/products/${id}`);
        const p = response.data;
        setProduct(p);

        // Default tab selection
        if (p.view_360?.enabled && p.view_360?.frames?.length > 0) {
          setActiveMediaTab('360');
        } else if (p.video_showcase?.enabled) {
          setActiveMediaTab('video');
        } else {
          setActiveMediaTab('gallery');
        }

        // Fetch similar products
        try {
          const simRes = await api.get(`/api/products/${id}/similar?limit=4`);
          setSimilarProducts(simRes.data || []);
        } catch (e) {
          console.warn("Could not fetch similar products", e);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load product details.');
      } finally {
        setIsLoading(false);
      }
    };
    if (id) fetchProduct();
  }, [id]);

  const handleAddToCart = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (!product || product.current_stock <= 0) return;

    setAddingToCart(true);
    setCartSuccessMessage('');
    try {
      await api.post('/api/cart/items', {
        product_id: product.id,
        variant_id: product.variants?.[0]?.id,
        sku: product.variants?.[0]?.sku,
        quantity: 1
      });
      window.dispatchEvent(new CustomEvent('cart-updated'));
      setCartSuccessMessage('Item added to cart!');
      setTimeout(() => setCartSuccessMessage(''), 4000);
    } catch (err: any) {
      console.error('Failed to add to cart', err);
      if (err.response?.status === 400) {
        setIsAlternativeModalOpen(true);
      }
    } finally {
      setAddingToCart(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-10 h-10 border-3 border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin"></div>
        <p className="text-[13px] tracking-[-0.017em] text-[#787574]">
          Loading product constellation...
        </p>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="max-w-xl mx-auto my-16 bg-[#ffffff] rounded-[28px] p-8 text-center border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] space-y-4">
        <AlertCircle className="w-12 h-12 text-[#5433eb] mx-auto" />
        <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">Product Not Found</h2>
        <p className="text-[13px] tracking-[-0.017em] text-[#787574]">{error || 'This product does not exist in the catalog.'}</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2.5 bg-[#5433eb] text-[#ffffff] rounded-[9999px] text-[13px] font-semibold tracking-[-0.017em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] cursor-pointer"
        >
          Return to Catalog
        </button>
      </div>
    );
  }

  const isOutOfStock = product.current_stock <= 0;

  return (
    <div className="space-y-12 pb-24 max-w-7xl mx-auto px-4 sm:px-6 pt-4">
      
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 px-4 py-2 rounded-[9999px] bg-[#ffffff] hover:bg-[#f2f4f5] text-[#000000] text-[13px] font-medium tracking-[-0.017em] border border-[#ebebeb] shadow-[0_2px_8px_rgba(0,0,0,0.06)] transition-all cursor-pointer"
        >
          <ArrowLeft size={15} />
          <span>Back to products</span>
        </button>

        <span className="text-[12px] font-mono text-[#787574] hidden sm:block">
          SKU: {product.sku || product.id.slice(0, 8).toUpperCase()}
        </span>
      </div>

      {/* Main Product Showcase Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Multimodal Experience Tabs & Viewer (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* Media Switcher Tab Ribbon */}
          <div className="flex flex-wrap gap-2 p-1.5 bg-[#ffffff] rounded-[9999px] border border-[#ebebeb] shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
            <button
              onClick={() => setActiveMediaTab('gallery')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-4 rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] transition-all cursor-pointer ${
                activeMediaTab === 'gallery'
                  ? 'bg-[#5433eb] text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)]'
                  : 'text-[#000000] hover:bg-[#f2f4f5]'
              }`}
            >
              <ImageIcon size={14} />
              <span>Photo Gallery</span>
            </button>

            <button
              onClick={() => setActiveMediaTab('360')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-4 rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] transition-all cursor-pointer ${
                activeMediaTab === '360'
                  ? 'bg-[#5433eb] text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)]'
                  : 'text-[#000000] hover:bg-[#f2f4f5]'
              }`}
            >
              <RotateCw size={14} />
              <span>360° Studio</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-[9999px] ${
                activeMediaTab === '360' ? 'bg-[#ffffff]/20 text-[#ffffff]' : 'bg-[#c0b5f3]/40 text-[#5433eb]'
              }`}>
                24 Frames
              </span>
            </button>

            <button
              onClick={() => setActiveMediaTab('video')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-4 rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] transition-all cursor-pointer ${
                activeMediaTab === 'video'
                  ? 'bg-[#5433eb] text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)]'
                  : 'text-[#000000] hover:bg-[#f2f4f5]'
              }`}
            >
              <PlaySquare size={14} />
              <span>Video Showcase</span>
            </button>
          </div>

          {/* Active Multimodal Component Stage */}
          <div className="w-full">
            {activeMediaTab === 'gallery' && (
              <MediaGallery
                images={product.gallery || []}
                productTitle={product.title || product.name || 'Product'}
              />
            )}

            {activeMediaTab === '360' && (
              <ThreeSixtyViewer
                config={product.view_360}
                productTitle={product.title || product.name || 'Product'}
              />
            )}

            {activeMediaTab === 'video' && (
              <ProductVideoPlayer
                config={product.video_showcase}
                title={product.title || product.name || 'Product'}
              />
            )}
          </div>
        </div>

        {/* Right Column: Product Info & Commerce Engine (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          
          <div className="bg-[#ffffff] rounded-[28px] p-6 sm:p-8 border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] space-y-6">
            
            {/* Brand & Title */}
            <div>
              <div className="text-[13px] font-semibold tracking-[-0.017em] text-[#5433eb] uppercase mb-1">
                {product.brand || 'SmartCommerce Flagship'}
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-[-0.05em] text-[#000000] leading-tight">
                {product.title || product.name}
              </h1>
            </div>

            {/* Ratings & Social Proof */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1 bg-[#f2f4f5] rounded-[9999px]">
                <Star className="fill-[#000000] text-[#000000]" size={13} />
                <span className="text-[12px] font-bold tracking-[-0.017em] text-[#000000]">
                  {(product.rating_avg || 4.8).toFixed(1)}
                </span>
              </div>
              <span className="text-[13px] tracking-[-0.017em] text-[#787574]">
                {product.review_count || 142} customer reviews
              </span>
            </div>

            {/* Price Stack */}
            <div className="flex items-baseline gap-3 pt-2 border-t border-[#ebebeb]">
              <div className="text-3xl sm:text-4xl font-bold tracking-[-0.05em] text-[#000000]">
                {typeof product.price === 'number' && Number.isFinite(product.price)
                  ? `$${product.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                  : 'Price unavailable'}
              </div>
              {typeof product.price === 'number' && product.compare_at_price && product.compare_at_price > product.price && (
                <div className="text-[16px] text-[#787574] line-through tracking-[-0.017em]">
                  ${product.compare_at_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              )}
            </div>

            {/* Live Inventory Status */}
            <div>
              {isOutOfStock ? (
                <div className="p-3.5 rounded-[20px] bg-[#f2f4f5] border border-[#ebebeb] space-y-2">
                  <div className="flex items-center gap-2 text-[#000000] font-semibold text-[13px] tracking-[-0.017em]">
                    <AlertCircle size={16} className="text-[#5433eb]" />
                    <span>Currently Out of Stock at Main Warehouse</span>
                  </div>
                  <p className="text-[12px] tracking-[-0.017em] text-[#787574]">
                    Our AI RecSys automatically found matching in-stock warehouse alternatives.
                  </p>
                  <button
                    onClick={() => setIsAlternativeModalOpen(true)}
                    className="w-full py-2 bg-[#5433eb] text-[#ffffff] rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] cursor-pointer"
                  >
                    View In-Stock Alternatives
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-[#000000] text-[13px] font-medium tracking-[-0.017em]">
                  <CheckCircle2 size={16} className="text-[#5433eb]" />
                  <span>In Stock • Ready for immediate fulfillment ({product.current_stock} units available)</span>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-2">
              <button
                onClick={handleAddToCart}
                disabled={isOutOfStock || addingToCart}
                className={`w-full py-3.5 rounded-[9999px] text-[15px] font-semibold tracking-[-0.031em] flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  isOutOfStock
                    ? 'bg-[#cccccc] text-[#787574] cursor-not-allowed'
                    : 'bg-[#5433eb] hover:brightness-110 active:scale-[0.98] text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)]'
                }`}
              >
                <ShoppingCart size={18} />
                <span>{addingToCart ? 'Adding...' : isOutOfStock ? 'Sold Out' : 'Add to Cart'}</span>
              </button>

              {cartSuccessMessage && (
                <div className="p-3 rounded-[9999px] bg-[#c0b5f3]/25 text-[#5433eb] text-center text-[12px] font-semibold tracking-[-0.017em] animate-in fade-in">
                  ✓ {cartSuccessMessage}
                </div>
              )}
            </div>

            {/* Description */}
            {product.description && (
              <div className="pt-4 border-t border-[#ebebeb] space-y-2">
                <h3 className="text-[14px] font-bold tracking-[-0.014em] text-[#000000]">About this item</h3>
                <p className="text-[13px] tracking-[-0.017em] text-[#787574] leading-relaxed">
                  {product.description}
                </p>
              </div>
            )}

            {/* Hardware Specifications */}
            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="pt-4 border-t border-[#ebebeb] space-y-3">
                <h3 className="text-[14px] font-bold tracking-[-0.014em] text-[#000000] flex items-center gap-1.5">
                  <Cpu size={15} className="text-[#5433eb]" />
                  <span>Technical Specifications</span>
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {Object.entries(product.specifications).map(([key, val]) => (
                    <div key={key} className="p-3 rounded-[16px] bg-[#f2f4f5] border border-[#ebebeb]/60">
                      <div className="text-[11px] font-medium text-[#787574] capitalize tracking-[-0.017em]">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-[12px] font-semibold text-[#000000] tracking-[-0.017em] mt-0.5">
                        {String(val)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>

      {/* Similar Recommended Products Section */}
      {similarProducts.length > 0 && (
        <section className="space-y-4 pt-8 border-t border-[#ebebeb]">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-[#5433eb]" />
            <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
              Similar Items You May Like
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {similarProducts.map((p) => {
              const primaryImg = p.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80';
              return (
                <ProductCard
                  key={p.id}
                  id={p.id}
                  title={p.title || p.name || 'Product'}
                  brand={p.brand || 'SmartCommerce'}
                  price={p.price}
                  imageUrl={primaryImg}
                  rating={p.rating_avg || 4.7}
                  reviewCount={p.review_count || 64}
                  has360={true}
                  hasVideo={true}
                  onClick={() => {
                    navigate(`/product/${p.id}`);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                />
              );
            })}
          </div>
        </section>
      )}

      {/* Customer Reviews Section */}
      <section className="space-y-6 pt-8 border-t border-[#ebebeb]">
        <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
          Customer Reviews
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-5xl font-bold tracking-tight text-[#000000]">{(product.rating_avg || 4.8).toFixed(1)}</span>
              <div className="space-y-1">
                <div className="flex items-center text-[#000000]">
                  <Star className="fill-[#000000]" size={16} />
                  <Star className="fill-[#000000]" size={16} />
                  <Star className="fill-[#000000]" size={16} />
                  <Star className="fill-[#000000]" size={16} />
                  <Star className="fill-[#000000] text-gray-300" size={16} />
                </div>
                <div className="text-[13px] text-[#787574]">{product.review_count || 142} global ratings</div>
              </div>
            </div>
            <button className="w-full py-2.5 border-2 border-[#000000] text-[#000000] rounded-full text-[14px] font-bold hover:bg-[#f2f4f5] transition">
              Write a Review
            </button>
          </div>
          
          <div className="md:col-span-2 space-y-6">
            {[1, 2].map((i) => (
              <div key={i} className="pb-6 border-b border-[#ebebeb] last:border-0">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-8 rounded-full bg-[#f2f4f5] flex items-center justify-center font-bold text-[#000000] text-[12px]">
                    JD
                  </div>
                  <span className="font-semibold text-[14px] text-[#000000]">Verified Buyer</span>
                  <div className="flex text-[#000000] ml-auto">
                    <Star className="fill-[#000000]" size={14} />
                    <Star className="fill-[#000000]" size={14} />
                    <Star className="fill-[#000000]" size={14} />
                    <Star className="fill-[#000000]" size={14} />
                    <Star className="fill-[#000000]" size={14} />
                  </div>
                </div>
                <h4 className="font-bold text-[14px] text-[#000000] mb-1">Excellent build quality and design</h4>
                <p className="text-[13px] text-[#787574] leading-relaxed">
                  "I was initially hesitant about the price, but the quality here is undeniable. 
                  The minimalist aesthetic fits perfectly into my setup, and it functions exactly as described. 
                  Highly recommended for anyone looking for a premium experience."
                </p>
                <div className="mt-3 text-[12px] text-[#787574]">Reviewed in the United States on Sept 14, 2026</div>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* In-Stock Alternative Modal */}
      {isAlternativeModalOpen && (
        <InStockAlternativeModal
          outOfStockProduct={{
            id: product.id,
            title: product.title || product.name || 'Product',
            price: product.price ?? 0,
            category_id: ''
          }}
          isOpen={true}
          onClose={() => setIsAlternativeModalOpen(false)}
          onSelectAlternative={(altId) => {
            setIsAlternativeModalOpen(false);
            navigate(`/product/${altId}`);
          }}
        />
      )}

    </div>
  );
};
export default ProductDetails;
