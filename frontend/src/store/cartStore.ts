import { create } from 'zustand';

interface CartItem {
  id: string;
  product: {
    id: string;
    name: string;
    price: number;
    image?: string;
  };
  quantity: number;
}

interface CartState {
  items: CartItem[];
  total: number;
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  total: 0,
  addItem: (item) => {
    const existing = get().items.find(i => i.id === item.id);
    if (existing) {
      set(state => ({
        items: state.items.map(i => i.id === item.id ? { ...i, quantity: i.quantity + item.quantity } : i),
        total: state.total + item.product.price * item.quantity,
      }));
    } else {
      set(state => ({
        items: [...state.items, item],
        total: state.total + item.product.price * item.quantity,
      }));
    }
  },
  removeItem: (id) => {
    const item = get().items.find(i => i.id === id);
    set(state => ({
      items: state.items.filter(i => i.id !== id),
      total: state.total - (item ? item.product.price * item.quantity : 0),
    }));
  },
  clearCart: () => set({ items: [], total: 0 }),
}));
