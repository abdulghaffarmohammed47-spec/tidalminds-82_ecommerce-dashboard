import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CreditCard, ShieldCheck, CheckCircle2, Package,
  ArrowRight, AlertCircle, Loader2
} from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface CartItem {
  id: string;
  product_id: string;
  quantity: number;
  price_at_add?: number;
  title?: string;
  price?: number;
  image_url?: string;
}

type CheckoutStep = 'loading' | 'payment' | 'confirming' | 'success' | 'empty' | 'error';

export const Checkout: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const [step, setStep] = useState<CheckoutStep>('loading');
  const [items, setItems] = useState<CartItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [placedOrderId, setPlacedOrderId] = useState<string | null>(null);
  const [couponCode, setCouponCode] = useState('');
  const [couponMessage, setCouponMessage] = useState<string | null>(null);
  const [couponDiscount, setCouponDiscount] = useState(0);

  // ── Fetch live cart on mount ─────────────────────────────────────────────
  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    (async () => {
      try {
        const cartRes = await api.get('/api/cart');
        const cartItems: CartItem[] = cartRes.data.items || [];
        if (cartItems.length === 0) { setStep('empty'); return; }

        // Enrich with product details (name + price)
        const enriched = await Promise.all(
          cartItems.map(async (item) => {
            try {
              const p = (await api.get(`/api/products/${item.product_id}`)).data;
              return {
                ...item,
                title: p.title || p.name || 'Product',
                price: Number(item.price_at_add ?? p.price ?? 0) / 100,
                image_url: p.gallery?.[0]?.url || undefined,
              };
            } catch {
              return { ...item, title: 'Product', price: 0 };
            }
          })
        );
        setItems(enriched);
        setStep('payment');
      } catch (err) {
        setError('Failed to load your cart. Please try again.');
        setStep('error');
      }
    })();
  }, [user, navigate]);

  // ── Payment submit ────────────────────────────────────────────────────────
  const handlePay = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setStep('confirming');
    try {
      // Step 1: Create order from cart
      const orderRes = await api.post('/api/orders/checkout', {
        coupon_code: couponCode.trim() || undefined,
      });
      const orderId: string = orderRes.data.id;

      // Step 2: Simulate payment success
      await api.post(`/api/payments/${orderId}/simulate`, { success: true });

      // Notify Navbar that cart has been cleared
      window.dispatchEvent(new CustomEvent('cart-updated'));

      setPlacedOrderId(orderId);
      setStep('success');
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Payment failed. Please try again.';
      setError(Array.isArray(msg) ? msg[0]?.msg || String(msg) : String(msg));
      setStep('payment');
    }
  };

  const subtotal = items.reduce((s, i) => s + (i.price || 0) * i.quantity, 0);
  const tax = subtotal * 0.08;
  const total = Math.max(0, subtotal + tax - couponDiscount);

  const handleApplyCoupon = async () => {
    const code = couponCode.trim();
    if (!code) return;
    setCouponMessage(null);
    setCouponDiscount(0);
    try {
      const response = await api.post('/api/v1/coupons/validate', { code });
      const coupon = response.data;
      const discount = coupon.discount_type === 'PERCENTAGE'
        ? Math.min(subtotal * coupon.discount_value / 100, coupon.max_discount_amount == null ? Number.MAX_SAFE_INTEGER : coupon.max_discount_amount / 100)
        : coupon.discount_value / 100;
      setCouponDiscount(Math.min(discount, subtotal));
      setCouponMessage(`Coupon ${coupon.code} applied`);
    } catch (err: any) {
      setCouponMessage(err.response?.data?.detail || 'Coupon is not valid');
    }
  };

  // ── States ────────────────────────────────────────────────────────────────

  if (step === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-8 h-8 border-[3px] border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin" />
        <p className="text-[13px] text-[#787574]">Preparing your checkout…</p>
      </div>
    );
  }

  if (step === 'empty') {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-4">
        <Package size={40} className="mx-auto text-[#ebebeb]" />
        <h1 className="text-[22px] font-bold text-[#000]">Nothing to checkout</h1>
        <p className="text-[13px] text-[#787574]">Your cart is empty. Add something first!</p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2.5 bg-[#5433eb] text-white rounded-full text-[13px] font-semibold hover:brightness-110 transition"
        >
          Browse Catalog
        </button>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="max-w-md mx-auto my-16 bg-[#ffffff] rounded-[32px] p-10 text-center border border-[#ebebeb] shadow-lg space-y-5">
        <div className="w-20 h-20 rounded-full bg-[#5433eb]/10 text-[#5433eb] flex items-center justify-center mx-auto">
          <CheckCircle2 size={40} />
        </div>
        <h1 className="text-[26px] font-bold tracking-[-0.04em] text-[#000]">Order Confirmed!</h1>
        <p className="text-[13px] text-[#787574] leading-relaxed">
          Your ACID-locked inventory reservation has been committed. Your order is now in fulfillment.
        </p>
        {placedOrderId && (
          <div className="px-4 py-2 bg-[#f2f4f5] rounded-[12px] text-[11px] font-mono text-[#787574] break-all">
            Order #{placedOrderId.slice(0, 8).toUpperCase()}
          </div>
        )}
        <div className="flex gap-3 pt-2">
          <button
            onClick={() => navigate('/orders')}
            className="flex-1 py-3 bg-[#5433eb] text-white rounded-full text-[13px] font-semibold hover:brightness-110 transition shadow-[0_4px_24px_rgba(84,51,235,0.35)]"
          >
            View My Orders
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex-1 py-3 border border-[#ebebeb] rounded-full text-[13px] font-semibold text-[#000] hover:bg-[#f2f4f5] transition"
          >
            Keep Shopping
          </button>
        </div>
      </div>
    );
  }

  if (step === 'error' && !items.length) {
    return (
      <div className="max-w-md mx-auto py-20 text-center space-y-4">
        <AlertCircle size={40} className="mx-auto text-red-400" />
        <h1 className="text-[18px] font-bold text-[#000]">Something went wrong</h1>
        <p className="text-[13px] text-[#787574]">{error}</p>
        <button onClick={() => navigate('/cart')} className="text-[#5433eb] hover:underline text-[13px] font-semibold">
          Back to cart
        </button>
      </div>
    );
  }

  // ── Payment form ──────────────────────────────────────────────────────────
  const isConfirming = step === 'confirming';

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-[28px] font-bold tracking-[-0.04em] text-[#000]">Secure Checkout</h1>
        <p className="text-[13px] text-[#787574] mt-0.5">
          Powered by ACID PostgreSQL row-locks • All transactions are atomic
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* ── Payment Form ── */}
        <div className="md:col-span-2">
          <form
            onSubmit={handlePay}
            className="bg-[#ffffff] rounded-[28px] p-8 border border-[#ebebeb] shadow-sm space-y-6"
          >
            <h2 className="text-[16px] font-bold flex items-center gap-2">
              <CreditCard size={18} className="text-[#5433eb]" />
              Payment Information
            </h2>

            {error && (
              <div className="p-4 bg-red-50 text-red-600 rounded-[16px] text-[13px] flex items-start gap-2">
                <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                {error}
              </div>
            )}

            {/* Demo Card Notice */}
            <div className="p-3.5 bg-[#5433eb]/5 border border-[#5433eb]/20 rounded-[14px] text-[12px] text-[#5433eb]">
              <strong>Demo mode</strong> — any values work. Payment is simulated via the backend state machine.
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-[12px] font-semibold text-[#444] mb-1.5">Card Number</label>
                <input
                  type="text"
                  defaultValue="4242 4242 4242 4242"
                  className="w-full px-4 py-3 bg-[#f2f4f5] rounded-[14px] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 focus:bg-white transition font-mono"
                  required
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-[12px] font-semibold text-[#444] mb-1.5">Expiry</label>
                  <input
                    type="text"
                    defaultValue="09/28"
                    className="w-full px-4 py-3 bg-[#f2f4f5] rounded-[14px] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 focus:bg-white transition"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[12px] font-semibold text-[#444] mb-1.5">CVC</label>
                  <input
                    type="text"
                    defaultValue="123"
                    className="w-full px-4 py-3 bg-[#f2f4f5] rounded-[14px] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 focus:bg-white transition"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-[12px] font-semibold text-[#444] mb-1.5">Name on Card</label>
                <input
                  type="text"
                  placeholder="Full name"
                  className="w-full px-4 py-3 bg-[#f2f4f5] rounded-[14px] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 focus:bg-white transition"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isConfirming}
              className="w-full py-4 bg-[#000000] text-white rounded-full text-[15px] font-bold hover:bg-[#222] active:scale-[0.98] transition disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-[0_4px_20px_rgba(0,0,0,0.15)]"
            >
              {isConfirming ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Processing Payment…
                </>
              ) : (
                <>
                  Pay ₹{total.toFixed(2)}
                  <ArrowRight size={16} />
                </>
              )}
            </button>

            <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#787574]">
              <ShieldCheck size={13} className="text-[#5433eb]" />
              256-bit SSL encryption · ACID guaranteed inventory lock
            </div>
          </form>
        </div>

        {/* ── Order Summary ── */}
        <div className="bg-[#f2f4f5] rounded-[28px] p-6 h-fit border border-[#ebebeb] space-y-4">
          <h3 className="font-bold text-[15px] text-[#000]">Order Summary</h3>

          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.id} className="flex items-center gap-3">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.title}
                    className="w-11 h-11 rounded-[10px] object-cover bg-white flex-shrink-0"
                  />
                ) : (
                  <div className="w-11 h-11 rounded-[10px] bg-white flex-shrink-0" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] font-semibold text-[#000] truncate">{item.title}</p>
                  <p className="text-[11px] text-[#787574]">Qty {item.quantity}</p>
                </div>
                <span className="text-[12px] font-bold text-[#000] flex-shrink-0">
                  ₹{((item.price || 0) * item.quantity).toFixed(2)}
                </span>
              </div>
            ))}
          </div>

          <div className="border-t border-[#ebebeb] pt-3 space-y-2 text-[12px]">
            <div className="flex justify-between text-[#787574]">
              <span>Subtotal</span><span>₹{subtotal.toFixed(2)}</span>
            </div>

            <div className="border-t border-[#ebebeb] pt-3 space-y-2">
              <label htmlFor="coupon-code" className="text-[12px] font-semibold text-[#444]">Coupon code</label>
              <div className="flex gap-2">
                <input
                  id="coupon-code"
                  value={couponCode}
                  onChange={(event) => setCouponCode(event.target.value)}
                  placeholder="WELCOME10"
                  className="min-w-0 flex-1 px-3 py-2 bg-white rounded-[10px] text-[12px] border border-[#ebebeb] outline-none focus:ring-2 focus:ring-[#5433eb]/30"
                />
                <button type="button" onClick={handleApplyCoupon} className="px-3 py-2 bg-[#000] text-white rounded-[10px] text-[12px] font-semibold">Apply</button>
              </div>
              {couponMessage && <p className={`text-[11px] ${couponDiscount ? 'text-emerald-600' : 'text-red-500'}`}>{couponMessage}</p>}
              {couponDiscount > 0 && <div className="flex justify-between text-[#5433eb]"><span>Coupon discount</span><span>-₹{couponDiscount.toFixed(2)}</span></div>}
            </div>
            <div className="flex justify-between text-[#787574]">
              <span>Tax (8%)</span><span>₹{tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-[#787574]">
              <span>Shipping</span><span className="text-[#5433eb] font-semibold">FREE</span>
            </div>
          </div>

          <div className="border-t border-[#ebebeb] pt-3 flex justify-between font-bold text-[15px] text-[#000]">
            <span>Total</span>
            <span>₹{total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Checkout;
