import { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  ShoppingCart, Search, User, Sparkles, LogOut, Heart,
  LayoutDashboard, Store, ClipboardList
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import api from '../lib/api';

export const Navbar = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [cartCount, setCartCount] = useState(0);

  // Fetch live cart count whenever route changes, user changes, or cart-updated event fires
  useEffect(() => {
    const fetchCartCount = () => {
      if (!user) { setCartCount(0); return; }
      api.get('/api/cart')
        .then(res => {
          const items = res.data?.items ?? [];
          const count = items.reduce((s: number, i: { quantity: number }) => s + i.quantity, 0);
          setCartCount(count);
        })
        .catch(() => setCartCount(0));
    };

    fetchCartCount();
    window.addEventListener('cart-updated', fetchCartCount);
    return () => window.removeEventListener('cart-updated', fetchCartCount);
  }, [user, location.pathname]);

  const handleLogout = () => {
    logout();
    setCartCount(0);
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 px-4 sm:px-6 py-3 pointer-events-none">
      <nav className="pointer-events-auto max-w-7xl mx-auto bg-[#ffffff]/95 backdrop-blur-md rounded-[9999px] border border-[#ebebeb]/90 shadow-[0_2px_12px_rgba(0,0,0,0.06)] px-5 py-2.5 flex items-center justify-between transition-all">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group flex-shrink-0">
          <div className="w-9 h-9 rounded-[9999px] bg-[#5433eb] flex items-center justify-center text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)] group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="text-[17px] font-bold tracking-[-0.031em] text-[#000000]">
            Smart<span className="text-[#5433eb]">Commerce</span>
          </span>
        </Link>

        {/* Center Search */}
        <div className="flex-1 max-w-xl mx-6 hidden md:block">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const q = formData.get('q') as string;
              if (q?.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`);
            }}
            className="relative"
          >
            <input
              name="q"
              type="text"
              placeholder="Search products semantically…"
              className="w-full bg-[#f2f4f5] rounded-[9999px] px-4 py-2 pl-10 text-[13px] tracking-[-0.017em] text-[#000000] placeholder:text-[#787574] focus:outline-none focus:ring-2 focus:ring-[#5433eb]/40 focus:bg-[#ffffff] transition-all"
            />
            <Search className="absolute left-3.5 top-2.5 text-[#787574] w-4 h-4 pointer-events-none" />
          </form>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-1 sm:gap-2">

          {/* Cart */}
          <Link
            to="/cart"
            id="nav-cart-btn"
            className="relative text-[#000000] hover:text-[#5433eb] p-2 rounded-[9999px] hover:bg-[#f2f4f5] transition-colors"
            title="Shopping Cart"
          >
            <ShoppingCart className="w-5 h-5" />
            {cartCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#5433eb] text-white rounded-full text-[9px] font-bold flex items-center justify-center leading-none shadow">
                {cartCount > 99 ? '99' : cartCount}
              </span>
            )}
          </Link>
          <Link
            to="/wishlist"
            className="relative rounded-full p-2 text-[#172033] transition-colors hover:bg-[#f0efff] hover:text-[#6d5dfc]"
            title="Wishlist"
            aria-label="Wishlist"
          >
            <Heart className="h-5 w-5" />
          </Link>

          {user ? (
            <div className="flex items-center gap-1">
              {/* My Orders — visible to all logged-in users */}
              <Link
                to="/orders"
                id="nav-orders-btn"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[12px] font-semibold text-[#787574] hover:text-[#000] hover:bg-[#f2f4f5] transition"
                title="My Orders"
              >
                <ClipboardList size={14} />
                <span className="hidden lg:inline">Orders</span>
              </Link>

              {/* Seller Portal — seller role */}
              {user.role === 'seller' && (
                <Link
                  to="/seller"
                  id="nav-seller-btn"
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[12px] font-semibold text-[#787574] hover:text-[#5433eb] hover:bg-[#5433eb]/5 transition"
                  title="Seller Portal"
                >
                  <Store size={14} />
                  <span className="hidden lg:inline">Portal</span>
                </Link>
              )}

              {/* Admin — admin or seller (any non-customer shows dashboard) */}
              {(user.role === 'admin') && (
                <Link
                  to="/admin"
                  id="nav-admin-btn"
                  className="text-[#000000] hover:text-[#5433eb] p-2 rounded-[9999px] hover:bg-[#f2f4f5] transition-colors"
                  title="Admin Dashboard"
                >
                  <LayoutDashboard className="w-5 h-5" />
                </Link>
              )}

              {/* Avatar + Logout */}
              <div className="flex items-center gap-1 pl-1">
                <div className="w-8 h-8 rounded-[9999px] bg-[#c0b5f3]/40 border border-[#5433eb]/30 flex items-center justify-center text-[#5433eb] font-bold text-xs">
                  {(user.email?.charAt(0) || user.role?.charAt(0) || 'U').toUpperCase()}
                </div>
                <button
                  onClick={handleLogout}
                  id="nav-logout-btn"
                  className="text-[#787574] hover:text-[#000000] p-2 rounded-[9999px] hover:bg-[#f2f4f5] transition-colors cursor-pointer"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 px-4 py-1.5 bg-[#000000] hover:bg-[#332f2d] text-[#ffffff] rounded-[9999px] text-[13px] font-medium tracking-[-0.017em] transition-all shadow-sm"
            >
              <User className="w-4 h-4" />
              <span>Sign In</span>
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
};
export default Navbar;
