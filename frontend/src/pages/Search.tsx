import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sparkles, PackageX, History, Text } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';
import { HeroSearchBar } from '../components/HeroSearchBar';
import { ProductCard } from '../components/ProductCard';
import { InStockAlternativeModal } from '../components/InStockAlternativeModal';

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
  has_360_view?: boolean;
  has_video?: boolean;
  view_360?: { enabled: boolean };
  gallery?: Array<{ url: string }>;
}

export const Search: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialCat = searchParams.get('category') || '';

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<Product[]>([]);
  const [recentQueries, setRecentQueries] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [filterInStockOnly, setFilterInStockOnly] = useState(false);
  const [searchMode, setSearchMode] = useState<'semantic' | 'keyword'>('semantic');
  
  // Alternative modal state
  const [selectedOutOfStockProduct, setSelectedOutOfStockProduct] = useState<Product | null>(null);

  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  // Fetch recent searches
  const fetchRecentSearches = async () => {
    try {
      const res = await api.get('/api/search/recent?limit=8');
      setRecentQueries(res.data || []);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    fetchRecentSearches();
  }, [user]);

  // Execute search function
  const executeSearch = async (searchQuery: string, catId?: string) => {
    if (!searchQuery.trim() && !catId) return;

    setIsSearching(true);
    setHasSearched(true);
    try {
      let endpoint = '';
      if (searchQuery.trim()) {
        endpoint = searchMode === 'semantic'
          ? `/api/search/semantic?query=${encodeURIComponent(searchQuery)}&limit=16`
          : `/api/products?search=${encodeURIComponent(searchQuery)}&limit=16`;
      } else if (catId) {
        endpoint = `/api/products?category_id=${catId}&limit=16`;
      }
      const response = await api.get(endpoint);
      setResults(response.data || []);
      fetchRecentSearches();
    } catch (error) {
      console.error('Search failed', error);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Run initial search if URL params present
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
      executeSearch(initialQuery);
    } else if (initialCat) {
      executeSearch('', initialCat);
    }
  }, [initialQuery, initialCat]);

  const handleSearchSubmit = (newQuery: string) => {
    setQuery(newQuery);
    setSearchParams({ q: newQuery });
    executeSearch(newQuery);
  };

  const handleChipClick = (q: string) => {
    setQuery(q);
    setSearchParams({ q });
    executeSearch(q);
  };

  const handleProductClick = (product: Product) => {
    if (product.current_stock <= 0) {
      setSelectedOutOfStockProduct(product);
    } else {
      navigate(`/product/${product.id}`);
    }
  };

  const displayedResults = filterInStockOnly
    ? results.filter((p) => p.current_stock > 0)
    : results;

  return (
    <div className="space-y-10 pb-24 max-w-7xl mx-auto px-4 sm:px-6 pt-6">
      
      {/* Search Header Constellation */}
      <div className="space-y-6 text-center max-w-3xl mx-auto">
        <h1 className="text-3xl sm:text-4xl font-bold tracking-[-0.05em] text-[#000000]">
          Search the <span className="text-[#5433eb]">Constellation</span>
        </h1>
        <p className="text-[15px] tracking-[-0.017em] text-[#787574]">
          Natural language semantic search powered by pgvector HNSW embeddings
        </p>

        {/* Hero Search Bar */}
        <HeroSearchBar onSearch={handleSearchSubmit} initialValue={query} />

        {/* Recent Searches Pill Stream */}
        {recentQueries.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            <span className="text-[12px] tracking-[-0.017em] text-[#787574] flex items-center gap-1">
              <History size={13} />
              Recent:
            </span>
            {recentQueries.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleChipClick(item)}
                className="px-3 py-1 rounded-[9999px] bg-[#ffffff] hover:bg-[#5433eb] text-[#000000] hover:text-[#ffffff] text-[12px] font-medium tracking-[-0.017em] border border-[#ebebeb] shadow-[0_2px_6px_rgba(0,0,0,0.04)] transition-all cursor-pointer"
              >
                {item}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Mode Toggle + Filter Bar */}
      {hasSearched && (
        <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-[#ebebeb]">
          <div className="text-[14px] font-semibold tracking-[-0.014em] text-[#000000]">
            {isSearching ? (
              <span className="flex items-center gap-2 text-[#787574]">
                <Sparkles size={16} className="text-[#5433eb] animate-spin" />
                {searchMode === 'semantic' ? 'Computing vector similarities…' : 'Searching catalog…'}
              </span>
            ) : (
              <span>Found {displayedResults.length} matching products</span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Search mode toggle */}
            <div className="flex items-center gap-1 bg-[#f2f4f5] p-1 rounded-full">
              <button
                id="search-mode-semantic"
                onClick={() => setSearchMode('semantic')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold transition ${
                  searchMode === 'semantic'
                    ? 'bg-[#5433eb] text-white shadow-sm'
                    : 'text-[#787574] hover:text-[#000]'
                }`}
              >
                <Sparkles size={11} /> Semantic
              </button>
              <button
                id="search-mode-keyword"
                onClick={() => setSearchMode('keyword')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold transition ${
                  searchMode === 'keyword'
                    ? 'bg-[#000] text-white shadow-sm'
                    : 'text-[#787574] hover:text-[#000]'
                }`}
              >
                <Text size={11} /> Keyword
              </button>
            </div>

            {/* In-stock filter */}
            <button
              onClick={() => setFilterInStockOnly(!filterInStockOnly)}
              className={`px-4 py-1.5 rounded-[9999px] text-[12px] font-semibold tracking-[-0.017em] border transition-all cursor-pointer ${
                filterInStockOnly
                  ? 'bg-[#5433eb] text-[#ffffff] border-[#5433eb] shadow-[0_4px_24px_rgba(69,36,219,0.34)]'
                  : 'bg-[#ffffff] text-[#000000] border-[#ebebeb] hover:border-[#cccccc]'
              }`}
            >
              {filterInStockOnly ? '✓ In-Stock Only' : 'Filter In-Stock'}
            </button>
          </div>
        </div>
      )}

      {/* Search Results Grid */}
      {displayedResults.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {displayedResults.map((product) => {
            const primaryImg = product.gallery?.[0]?.url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=800&q=80';
            const isOutOfStock = product.current_stock <= 0;

            return (
              <ProductCard
                key={product.id}
                id={product.id}
                title={product.title || product.name || 'Product'}
                brand={product.brand || 'SmartCommerce'}
                price={product.price}
                imageUrl={primaryImg}
                rating={product.rating_avg || 4.7}
                reviewCount={product.review_count || 88}
                matchScore={product.match_score}
                explanation={isOutOfStock ? '⚠️ Out of Stock (Click for In-Stock Alternative)' : product.recommendation_reason}
                isAlternative={false}
                has360={true}
                hasVideo={true}
                onClick={() => handleProductClick(product)}
              />
            );
          })}
        </div>
      ) : hasSearched && !isSearching ? (
        <div className="bg-[#ffffff] rounded-[28px] p-12 text-center border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] max-w-lg mx-auto space-y-4">
          <div className="w-14 h-14 rounded-[9999px] bg-[#f2f4f5] text-[#787574] flex items-center justify-center mx-auto">
            <PackageX size={26} />
          </div>
          <h3 className="text-[18px] font-bold tracking-[-0.031em] text-[#000000]">
            No Direct Matches Found
          </h3>
          <p className="text-[13px] tracking-[-0.017em] text-[#787574]">
            Try broader terms like "laptop", "audio", "camera", or "wireless" to trigger our hybrid search.
          </p>
        </div>
      ) : null}

      {/* Out of Stock Alternative Suggestion Modal */}
      {selectedOutOfStockProduct && (
        <InStockAlternativeModal
          outOfStockProduct={{
            id: selectedOutOfStockProduct.id,
            title: selectedOutOfStockProduct.title || selectedOutOfStockProduct.name || 'Product',
            price: selectedOutOfStockProduct.price,
            category_id: ''
          }}
          isOpen={true}
          onClose={() => setSelectedOutOfStockProduct(null)}
          onSelectAlternative={(altId) => {
            setSelectedOutOfStockProduct(null);
            navigate(`/product/${altId}`);
          }}
        />
      )}

    </div>
  );
};
export default Search;
