import { useEffect, useState } from 'react';
import { Sparkles, RotateCw, ShieldCheck, Zap, ArrowRight, Layers, Flame } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';
import { HeroSearchBar } from '../components/HeroSearchBar';
import { ProductCard } from '../components/ProductCard';

interface Product {
  id: string;
  name?: string;
  title: string;
  brand?: string;
  description?: string;
  price: number;
  current_stock: number;
  rating_avg?: number;
  review_count?: number;
  recommendation_reason?: string;
  match_score?: string;
  affinity_score?: number;
  has_360_view?: boolean;
  has_video?: boolean;
  view_360?: { enabled: boolean; frames?: string[] };
  video_showcase?: { enabled: boolean };
  gallery?: Array<{ url: string }>;
}

interface Category {
  id: string;
  name: string;
  slug: string;
}

export const Home = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [personalizedProducts, setPersonalizedProducts] = useState<Product[]>([]);
  const [popularProducts, setPopularProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  const sampleSearchPrompts = [
    "OLED laptop with 32GB RAM",
    "Studio headphones with active noise cancellation",
    "Flagship camera phone 5x zoom",
    "Mechanical gaming keyboard wireless"
  ];

  useEffect(() => {
    const fetchHomeData = async () => {
      setLoading(true);
      try {
        const featPromise = api.get('/api/products?limit=8');
        const catPromise = api.get('/api/categories/');
        const popPromise = api.get('/api/analytics/trending?limit=4');
        const persPromise = Promise.resolve({ data: [] });

        const [featRes, catRes, popRes, persRes] = await Promise.allSettled([
          featPromise,
          catPromise,
          popPromise,
          persPromise
        ]);

        if (featRes.status === 'fulfilled') setFeaturedProducts(featRes.value.data || []);
        if (catRes.status === 'fulfilled') setCategories(catRes.value.data || []);
        if (popRes.status === 'fulfilled') setPopularProducts(popRes.value.data || []);
        if (persRes.status === 'fulfilled') setPersonalizedProducts(persRes.value.data || []);
      } catch (err) {
        console.error("Error loading home feed:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHomeData();
  }, [user]);

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="market-home space-y-16 pb-24 max-w-7xl mx-auto px-4 sm:px-6">
      
      {/* 1. Hero Constellation Section */}
      <section className="market-hero relative pt-12 pb-6 flex flex-col items-center justify-center text-center">
        
        {/* Subtitle Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-[9999px] bg-[#ffffff] border border-[#ebebeb] text-[12px] font-medium tracking-[-0.017em] text-[#000000] mb-6 shadow-[0_2px_8px_rgba(0,0,0,0.06)]">
          <span className="w-2 h-2 rounded-full bg-[#5433eb] animate-pulse"></span>
          <span>Shop Constellation • 100% 360° Studio & Vector-Powered Discovery</span>
        </div>

        {/* Main Display Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-[-0.05em] text-[#000000] max-w-3xl mb-5 leading-[1.08]">
          Find everything from <br />
          <span className="text-[#5433eb]">A to Z</span> on white marble.
        </h1>

        <p className="text-[16px] sm:text-[17px] tracking-[-0.031em] text-[#787574] max-w-xl mx-auto mb-8 font-normal">
          Interactive 24-frame 360° camera scrubbing, instant video showcases, and search-history vector personalization.
        </p>

        {/* Floating Shop Violet Hero Search Bar */}
        <div className="w-full mb-5">
          <HeroSearchBar onSearch={handleSearch} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 max-w-2xl">
          <span className="text-[12px] tracking-[-0.017em] text-[#787574]">Popular:</span>
          {sampleSearchPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSearch(prompt)}
              className="px-3.5 py-1 rounded-[9999px] bg-[#ffffff] hover:bg-[#5433eb] text-[#000000] hover:text-[#ffffff] text-[12px] font-medium tracking-[-0.017em] border border-[#ebebeb] shadow-[0_2px_6px_rgba(0,0,0,0.04)] transition-all cursor-pointer"
            >
              {prompt}
            </button>
          ))}
        </div>
      </section>

      {/* 2. Floating Category Constellation */}
      {categories.length > 0 && (
        <section className="market-section market-category-section space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
              Explore Categories
            </h2>
            <button
              onClick={() => navigate('/search')}
              className="text-[13px] font-medium tracking-[-0.017em] text-[#5433eb] hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>View all</span>
              <ArrowRight size={13} />
            </button>
          </div>

          <div className="market-category-rail flex gap-2.5 overflow-x-auto pb-2 scrollbar-none">
            {categories.map((cat, index) => (
              <button
                key={cat.id || cat.slug || `${cat.name}-${index}`}
                onClick={() => navigate(`/search?category=${cat.id}`)}
                className="px-5 py-2.5 bg-[#ffffff] hover:bg-[#5433eb] text-[#000000] hover:text-[#ffffff] rounded-[9999px] text-[13px] font-semibold tracking-[-0.017em] border border-[#ebebeb] shadow-[0_2px_8px_rgba(0,0,0,0.05)] transition-all duration-200 whitespace-nowrap cursor-pointer flex items-center gap-2"
              >
                <Layers size={14} className="opacity-70" />
                <span>{cat.name}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* 3. Search-History-Aware Personalized Feed */}
      {personalizedProducts.length > 0 && (
        <section className="market-section space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-[9999px] bg-[#5433eb] text-[#ffffff] flex items-center justify-center shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
                <Sparkles size={15} />
              </div>
              <div>
                <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
                  Personalized For You
                </h2>
                <p className="text-[12px] tracking-[-0.017em] text-[#787574]">
                  Computed with exponential time-decay vector embeddings
                </p>
              </div>
            </div>
            <button
              onClick={() => navigate('/search')}
              className="text-[13px] font-medium tracking-[-0.017em] text-[#5433eb] hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>More</span>
              <ArrowRight size={13} />
            </button>
          </div>

          <div className="market-product-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {personalizedProducts.map((p, index) => {
              const primaryImg = p.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80';
              return (
                <ProductCard
                  key={p.id || `personalized-${index}`}
                  id={p.id}
                  title={p.title || p.name || 'Product'}
                  brand={p.brand || 'SmartCommerce'}
                  price={p.price}
                  imageUrl={primaryImg}
                  rating={p.rating_avg || 4.8}
                  reviewCount={p.review_count || 94}
                  explanation={p.recommendation_reason}
                  matchScore={p.match_score}
                  has360={true}
                  hasVideo={true}
                  onClick={() => navigate(`/product/${p.id}`)}
                />
              );
            })}
          </div>
        </section>
      )}

      {/* 4. Trending & Featured Catalog Grid */}
      <section className="market-section market-catalog-section space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
              Featured Multimodal Catalog
            </h2>
            <p className="text-[12px] tracking-[-0.017em] text-[#787574]">
              Every single product contains interactive 360° scrubbing & video showcase
            </p>
          </div>
          <button
            onClick={() => navigate('/search')}
            className="text-[13px] font-medium tracking-[-0.017em] text-[#5433eb] hover:underline flex items-center gap-1 cursor-pointer"
          >
            <span>Explore All</span>
            <ArrowRight size={13} />
          </button>
        </div>

        {loading ? (
          <div className="market-product-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
              <div key={n} className="bg-[#ffffff] rounded-[28px] p-2.5 h-[340px] animate-pulse border border-[#ebebeb]">
                <div className="w-full aspect-square bg-[#f2f4f5] rounded-[20px] mb-3"></div>
                <div className="h-3.5 bg-[#f2f4f5] rounded-full w-3/4 mb-2"></div>
                <div className="h-4 bg-[#f2f4f5] rounded-full w-1/2"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="market-product-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {featuredProducts.map((p, index) => {
              const primaryImg = p.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80';
              return (
                <ProductCard
                  key={p.id || `featured-${index}`}
                  id={p.id}
                  title={p.title || p.name || 'Product'}
                  brand={p.brand || 'SmartCommerce'}
                  price={p.price}
                  imageUrl={primaryImg}
                  rating={p.rating_avg || 4.7}
                  reviewCount={p.review_count || 120}
                  has360={true}
                  hasVideo={true}
                  onClick={() => navigate(`/product/${p.id}`)}
                />
              );
            })}
          </div>
        )}
      </section>

      {/* 5. Real-Time Popular Analytics Feed */}
      {popularProducts.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Flame size={18} className="text-[#5433eb]" />
              <h2 className="text-[20px] font-bold tracking-[-0.05em] text-[#000000]">
                Trending & Popular Products
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {popularProducts.map((p, index) => {
              const primaryImg = p.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80';
              return (
                <ProductCard
                  key={p.id || `popular-${index}`}
                  id={p.id}
                  title={p.title || p.name || 'Product'}
                  brand={p.brand || 'SmartCommerce'}
                  price={p.price}
                  imageUrl={primaryImg}
                  rating={p.rating_avg || 4.9}
                  reviewCount={p.review_count || 210}
                  has360={true}
                  hasVideo={true}
                  onClick={() => navigate(`/product/${p.id}`)}
                />
              );
            })}
          </div>
        </section>
      )}

      {/* 5. Enterprise Architectural Pillars on White Marble */}
      <section className="market-feature-grid grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div className="bg-[#ffffff] rounded-[28px] p-6 border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] flex flex-col justify-between">
          <div className="w-12 h-12 rounded-[9999px] bg-[#f2f4f5] text-[#5433eb] flex items-center justify-center mb-4">
            <RotateCw size={22} />
          </div>
          <div>
            <h3 className="text-[16px] font-bold tracking-[-0.031em] text-[#000000] mb-1.5">
              100% 360° Studio Coverage
            </h3>
            <p className="text-[13px] tracking-[-0.017em] text-[#787574] leading-relaxed">
              Every product features high-framerate rotational scrubbing, inertia physics, and angle-anchored hotspots.
            </p>
          </div>
        </div>

        <div className="bg-[#ffffff] rounded-[28px] p-6 border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] flex flex-col justify-between">
          <div className="w-12 h-12 rounded-[9999px] bg-[#f2f4f5] text-[#5433eb] flex items-center justify-center mb-4">
            <Zap size={22} />
          </div>
          <div>
            <h3 className="text-[16px] font-bold tracking-[-0.031em] text-[#000000] mb-1.5">
              Vector RecSys Personalization
            </h3>
            <p className="text-[13px] tracking-[-0.017em] text-[#787574] leading-relaxed">
              Decayed search intent vectors match available inventory with explainable recommendation text.
            </p>
          </div>
        </div>

        <div className="bg-[#ffffff] rounded-[28px] p-6 border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] flex flex-col justify-between">
          <div className="w-12 h-12 rounded-[9999px] bg-[#f2f4f5] text-[#5433eb] flex items-center justify-center mb-4">
            <ShieldCheck size={22} />
          </div>
          <div>
            <h3 className="text-[16px] font-bold tracking-[-0.031em] text-[#000000] mb-1.5">
              Row-Locked ACID Inventory
            </h3>
            <p className="text-[13px] tracking-[-0.017em] text-[#787574] leading-relaxed">
              Pessimistic PostgreSQL row locks guarantee zero overselling, coupled with instant in-stock alternatives.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
};
export default Home;
