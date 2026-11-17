import { useEffect, useState } from 'react';
import { Heart, Trash2, ShoppingBag, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

type WishlistItem = {
  id: string;
  product_id: string;
  created_at: string;
  product: {
    id: string;
    name: string;
    description?: string;
    is_active: boolean;
  };
};

export default function Wishlist() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    api.get('/api/v1/wishlist')
      .then((response) => setItems(response.data || []))
      .finally(() => setLoading(false));
  }, [navigate, user]);

  const remove = async (productId: string) => {
    await api.delete(`/api/v1/wishlist/${productId}`);
    setItems((current) => current.filter((item) => item.product_id !== productId));
  };

  if (loading) {
    return <div className="mx-auto max-w-5xl py-24 text-center text-[#667085]">Loading your wishlist...</div>;
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8 pb-24">
      <header className="flex items-end justify-between gap-4 border-b border-[#e6e8ef] pb-6">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-[#6d5dfc]">Your collection</p>
          <h1 className="font-['Space_Grotesk'] text-4xl font-bold tracking-[-0.05em] text-[#172033]">Wishlist</h1>
          <p className="mt-2 text-sm text-[#667085]">Keep the products you are considering close at hand.</p>
        </div>
        <div className="rounded-full bg-[#eeeaff] px-4 py-2 text-sm font-bold text-[#5646df]">{items.length} saved</div>
      </header>

      {items.length === 0 ? (
        <section className="rounded-[28px] border border-dashed border-[#cfd3df] bg-white px-6 py-20 text-center shadow-[0_18px_60px_rgba(38,32,88,0.08)]">
          <Heart className="mx-auto mb-4 text-[#6d5dfc]" size={42} />
          <h2 className="text-xl font-bold text-[#172033]">Your wishlist is waiting</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-[#667085]">Save products while you browse, then come back when you are ready to decide.</p>
          <button onClick={() => navigate('/')} className="mt-6 inline-flex items-center gap-2 rounded-full bg-[#172033] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#6d5dfc]">
            Browse marketplace <ArrowRight size={16} />
          </button>
        </section>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <article key={item.id} className="group overflow-hidden rounded-[24px] border border-[#e6e8ef] bg-white p-5 shadow-[0_12px_40px_rgba(38,32,88,0.07)] transition hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(38,32,88,0.12)]">
              <div className="mb-5 flex h-40 items-center justify-center rounded-[18px] bg-[linear-gradient(135deg,#eef0ff,#f5fbfa)]">
                <ShoppingBag className="text-[#6d5dfc]" size={42} strokeWidth={1.5} />
              </div>
              <p className="mb-1 text-xs font-bold uppercase tracking-[0.12em] text-[#6d5dfc]">Saved product</p>
              <h2 className="line-clamp-2 text-lg font-bold text-[#172033]">{item.product.name}</h2>
              <p className="mt-2 line-clamp-2 min-h-10 text-sm text-[#667085]">{item.product.description || 'Explore this product and its current seller offers.'}</p>
              <div className="mt-5 flex items-center gap-2">
                <button onClick={() => navigate(`/product/${item.product_id}`)} className="flex-1 rounded-full bg-[#172033] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-[#6d5dfc]">View product</button>
                <button onClick={() => remove(item.product_id)} aria-label={`Remove ${item.product.name} from wishlist`} className="rounded-full border border-[#e6e8ef] p-2.5 text-[#667085] transition hover:border-red-200 hover:bg-red-50 hover:text-red-500">
                  <Trash2 size={17} />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
