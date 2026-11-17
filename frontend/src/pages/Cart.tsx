import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, Trash2, ArrowRight, ShieldCheck, Plus, Minus } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface CartItem {
  product_id: string;
  sku: string;        // route param for PUT/DELETE /api/cart/items/{sku}
  quantity: number;
  price_at_add?: number;
  title?: string;
  price?: number;
  image_url?: string;
}

export const Cart: React.FC = () => {
  const [items, setItems] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    fetchCart();
  }, [user, navigate]);

  const fetchCart = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/api/cart');
      const cartItems: CartItem[] = response.data.items || [];

      const itemsWithDetails = await Promise.all(
        cartItems.map(async (item) => {
          try {
            const productRes = await api.get(`/api/products/${item.product_id}`);
            const p = productRes.data;
            return {
              ...item,
              title: p.title || p.name || 'Product',
              price: Number(item.price_at_add ?? p.price ?? 0) / 100,
              image_url:
                p.gallery?.[0]?.url ||
                'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=400&q=80',
            };
          } catch {
            return { ...item, title: 'Product', price: 0 };
          }
        })
      );
      setItems(itemsWithDetails);
    } catch (error) {
      console.error('Failed to fetch cart', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = async (sku: string) => {
    setUpdatingId(sku);
    try {
      await api.delete(`/api/cart/items/${sku}`);
      setItems(prev => prev.filter(i => i.sku !== sku));
      window.dispatchEvent(new CustomEvent('cart-updated'));
    } catch (error) {
      console.error('Failed to remove item', error);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleQtyChange = async (item: CartItem, delta: number) => {
    const newQty = item.quantity + delta;
    if (newQty <= 0) {
      await handleRemove(item.sku);
      return;
    }
    setUpdatingId(item.sku);
    try {
      await api.put(`/api/cart/items/${item.sku}`, { quantity: newQty });
      setItems(prev => prev.map(i => i.sku === item.sku ? { ...i, quantity: newQty } : i));
      window.dispatchEvent(new CustomEvent('cart-updated'));
    } catch (error) {
      console.error('Failed to update quantity', error);
    } finally {
      setUpdatingId(null);
    }
  };

  const subtotal = items.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0);
  const tax = subtotal * 0.08;
  const total = subtotal + tax;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-[3px] border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin" />
        <p className="text-[13px] tracking-[-0.017em] text-[#787574]">Loading cart...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-[-0.05em] text-[#000000]">Your Shopping Cart</h1>
        <p className="text-[13px] tracking-[-0.017em] text-[#787574]">
          {items.length} item{items.length === 1 ? '' : 's'} in your bag
        </p>
      </div>

      {items.length === 0 ? (
        <div className="bg-[#ffffff] rounded-[28px] p-12 text-center border border-[#ebebeb] shadow-sm space-y-4">
          <div className="w-14 h-14 rounded-[9999px] bg-[#f2f4f5] text-[#787574] flex items-center justify-center mx-auto">
            <ShoppingBag size={24} />
          </div>
          <h2 className="text-[18px] font-bold tracking-[-0.031em] text-[#000000]">Your cart is empty</h2>
          <p className="text-[13px] tracking-[-0.017em] text-[#787574]">
            Explore our multimodal 360° catalog to add products.
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2.5 bg-[#5433eb] text-[#ffffff] rounded-[9999px] text-[13px] font-semibold tracking-[-0.017em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] cursor-pointer"
          >
            Start Shopping
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Cart Items */}
          <div className="lg:col-span-8 space-y-3">
            {items.map((item) => {
              const isUpdating = updatingId === item.sku;
              return (
                <div
                  key={item.sku}
                  className={`bg-[#ffffff] rounded-[24px] p-4 flex items-center gap-4 border border-[#ebebeb] shadow-sm transition-opacity ${isUpdating ? 'opacity-50' : ''}`}
                >
                  <img
                    src={item.image_url || 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=400&q=80'}
                    alt={item.title}
                    className="w-20 h-20 rounded-[18px] object-cover bg-[#f2f4f5] flex-shrink-0"
                  />

                  <div className="flex-1 min-w-0">
                    <h3 className="text-[14px] font-semibold tracking-[-0.014em] text-[#000000] truncate">
                      {item.title}
                    </h3>
                    <p className="text-[11px] font-mono text-[#787574] mt-0.5">{item.sku}</p>
                    <div className="text-[13px] font-bold tracking-[-0.014em] text-[#000000] mt-1">
                      ₹{((item.price || 0) * item.quantity).toFixed(2)}
                    </div>
                    <div className="text-[11px] text-[#787574]">₹{(item.price || 0).toFixed(2)} each</div>
                  </div>

                  {/* Qty Controls */}
                  <div className="flex items-center gap-2 bg-[#f2f4f5] rounded-full px-1 py-1">
                    <button
                      onClick={() => handleQtyChange(item, -1)}
                      disabled={isUpdating}
                      className="w-7 h-7 rounded-full flex items-center justify-center bg-white hover:bg-[#5433eb] hover:text-white transition disabled:opacity-40 shadow-sm"
                    >
                      <Minus size={13} />
                    </button>
                    <span className="text-[13px] font-bold text-[#000] w-5 text-center">{item.quantity}</span>
                    <button
                      onClick={() => handleQtyChange(item, +1)}
                      disabled={isUpdating}
                      className="w-7 h-7 rounded-full flex items-center justify-center bg-white hover:bg-[#5433eb] hover:text-white transition disabled:opacity-40 shadow-sm"
                    >
                      <Plus size={13} />
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemove(item.sku)}
                    disabled={isUpdating}
                    className="p-2.5 rounded-[9999px] bg-[#f2f4f5] hover:bg-red-50 text-[#787574] hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40"
                    title="Remove item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              );
            })}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-4 bg-[#ffffff] rounded-[28px] p-6 border border-[#ebebeb] shadow-sm space-y-5">
            <h2 className="text-[16px] font-bold tracking-[-0.031em] text-[#000000]">Order Summary</h2>

            <div className="space-y-2.5 text-[13px] tracking-[-0.017em] border-b border-[#ebebeb] pb-4">
              <div className="flex justify-between text-[#787574]">
                <span>Subtotal ({items.reduce((s, i) => s + i.quantity, 0)} items)</span>
                <span className="text-[#000000] font-medium">₹{subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-[#787574]">
                <span>Estimated Tax (8%)</span>
                <span className="text-[#000000] font-medium">₹{tax.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-[#787574]">
                <span>Shipping</span>
                <span className="text-[#5433eb] font-semibold">FREE</span>
              </div>
            </div>

            <div className="flex justify-between text-[16px] font-bold tracking-[-0.031em] text-[#000000]">
              <span>Total</span>
              <span>₹{total.toFixed(2)}</span>
            </div>

            <button
              onClick={() => navigate('/checkout')}
              className="w-full py-3.5 bg-[#5433eb] hover:brightness-110 active:scale-[0.98] text-[#ffffff] rounded-[9999px] text-[14px] font-semibold tracking-[-0.014em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              <span>Proceed to Checkout</span>
              <ArrowRight size={16} />
            </button>

            <div className="flex items-center gap-1.5 justify-center text-[11px] font-medium tracking-[-0.017em] text-[#787574]">
              <ShieldCheck size={14} className="text-[#5433eb]" />
              <span>ACID Row-Lock Guaranteed Checkout</span>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};
export default Cart;
