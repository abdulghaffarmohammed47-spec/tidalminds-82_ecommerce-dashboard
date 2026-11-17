import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Store, Package, Clock, DollarSign, AlertTriangle,
  Warehouse, ShoppingBag, Plus, RefreshCw, ChevronDown, ChevronRight,
  CheckCircle2, Truck, XCircle, BarChart3, ArrowUpRight, Edit3
} from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

// ─── Types ───────────────────────────────────────────────────────────────────

interface SellerMetrics {
  total_sales: number;
  total_sales_display: number;
  active_listings: number;
  pending_orders: number;
  total_orders: number;
  low_stock_items: number;
}

interface SellerOrderItem {
  id: string;
  variant_id: string;
  snapshot_name: string;
  snapshot_price: number;
  quantity: number;
}

interface SellerOrder {
  id: string;
  order_id: string;
  seller_id: string;
  status: string;
  subtotal: number;
  created_at: string | null;
  items: SellerOrderItem[];
}

interface SellerProduct {
  product_id: string;
  product_name: string;
  variant_id: string;
  sku: string;
  variant_name: string;
  price: number;
  is_active: boolean;
  on_hand: number;
  reserved: number;
  available: number;
  warehouse_id: string | null;
  warehouse_name: string | null;
  category_id: string;
  brand_id: string;
}

interface SellerWarehouse {
  id: string;
  seller_id: string;
  name: string;
}

type TabId = 'overview' | 'orders' | 'inventory' | 'warehouses';

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  PENDING:    { label: 'Pending',    color: 'bg-amber-100 text-amber-700 border-amber-200',    icon: <Clock size={12} /> },
  PROCESSING: { label: 'Processing', color: 'bg-blue-100 text-blue-700 border-blue-200',       icon: <RefreshCw size={12} /> },
  SHIPPED:    { label: 'Shipped',    color: 'bg-purple-100 text-purple-700 border-purple-200', icon: <Truck size={12} /> },
  DELIVERED:  { label: 'Delivered',  color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: <CheckCircle2 size={12} /> },
  CANCELLED:  { label: 'Cancelled',  color: 'bg-red-100 text-red-700 border-red-200',           icon: <XCircle size={12} /> },
};

const VALID_TRANSITIONS: Record<string, string[]> = {
  PENDING:    ['PROCESSING', 'CANCELLED'],
  PROCESSING: ['SHIPPED', 'CANCELLED'],
  SHIPPED:    ['DELIVERED'],
  DELIVERED:  [],
  CANCELLED:  [],
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, color: 'bg-gray-100 text-gray-700 border-gray-200', icon: null };
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${cfg.color}`}>
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

function Spinner({ size = 'md' }: { size?: 'sm' | 'md' }) {
  const dim = size === 'sm' ? 'w-4 h-4 border-2' : 'w-7 h-7 border-[3px]';
  return <div className={`${dim} border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin`} />;
}

// ─── KPI Card ─────────────────────────────────────────────────────────────────

function KpiCard({ icon, label, value, sub, accent = false, warn = false }: {
  icon: React.ReactNode; label: string; value: string | number;
  sub?: string; accent?: boolean; warn?: boolean;
}) {
  const iconBg = warn ? 'bg-red-50 text-red-500' : accent ? 'bg-[#5433eb] text-white shadow-[0_4px_14px_rgba(84,51,235,0.35)]' : 'bg-[#f2f4f5] text-[#5433eb]';
  return (
    <div className="bg-white rounded-[20px] p-5 border border-[#ebebeb] shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-10 h-10 rounded-[12px] flex items-center justify-center ${iconBg}`}>
          {icon}
        </div>
        {sub && <span className="text-[11px] text-[#787574] bg-[#f2f4f5] px-2 py-0.5 rounded-full">{sub}</span>}
      </div>
      <p className="text-[28px] font-bold tracking-[-0.04em] text-[#000]">{value}</p>
      <p className="text-[12px] text-[#787574] mt-1 font-medium">{label}</p>
    </div>
  );
}

// ─── Add Product Modal ────────────────────────────────────────────────────────

function AddProductModal({ warehouses, onClose, onCreated }: {
  warehouses: SellerWarehouse[];
  onClose: () => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    name: '', description: '', sku: '', variant_name: '',
    price: '', initial_stock: '', category_id: '', brand_id: '',
    warehouse_id: warehouses[0]?.id ?? '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!form.category_id || !form.brand_id) { setError('Category ID and Brand ID are required.'); return; }
    try {
      setLoading(true);
      await api.post('/api/sellers/me/products', {
        ...form,
        price: Math.round(parseFloat(form.price) * 100),
        initial_stock: parseInt(form.initial_stock) || 0,
      });
      onCreated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Failed to create product');
    } finally {
      setLoading(false);
    }
  };

  const field = (label: string, key: keyof typeof form, type = 'text', placeholder = '') => (
    <div>
      <label className="block text-[12px] font-semibold text-[#444] mb-1">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        placeholder={placeholder}
        className="w-full px-3 py-2 rounded-[10px] border border-[#ebebeb] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 bg-[#fafafa]"
        required
      />
    </div>
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-[24px] w-full max-w-lg shadow-2xl overflow-hidden">
        <div className="px-6 py-5 border-b border-[#ebebeb] flex items-center justify-between">
          <h2 className="text-[17px] font-bold tracking-[-0.03em]">Add New Product</h2>
          <button onClick={onClose} className="text-[#787574] hover:text-black text-xl leading-none">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-3 max-h-[70vh] overflow-y-auto">
          {field('Product Name', 'name', 'text', 'e.g. Wireless Headphones')}
          {field('Description', 'description', 'text', 'Short product description')}
          <div className="grid grid-cols-2 gap-3">
            {field('SKU', 'sku', 'text', 'e.g. WH-001')}
            {field('Variant Name', 'variant_name', 'text', 'e.g. Black, 128GB')}
          </div>
          <div className="grid grid-cols-2 gap-3">
            {field('Price (₹)', 'price', 'number', '299.99')}
            {field('Initial Stock', 'initial_stock', 'number', '50')}
          </div>
          {field('Category ID', 'category_id', 'text', 'UUID from /api/categories/')}
          {field('Brand ID', 'brand_id', 'text', 'UUID from /api/products/brands')}
          <div>
            <label className="block text-[12px] font-semibold text-[#444] mb-1">Warehouse</label>
            <select
              value={form.warehouse_id}
              onChange={e => setForm(f => ({ ...f, warehouse_id: e.target.value }))}
              className="w-full px-3 py-2 rounded-[10px] border border-[#ebebeb] text-[13px] bg-[#fafafa] outline-none focus:ring-2 focus:ring-[#5433eb]/30"
            >
              {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
            </select>
          </div>
          {error && <p className="text-[12px] text-red-500 bg-red-50 px-3 py-2 rounded-[8px]">{error}</p>}
        </form>
        <div className="px-6 py-4 border-t border-[#ebebeb] flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-[13px] rounded-full border border-[#ebebeb] hover:bg-[#f2f4f5] transition">Cancel</button>
          <button
            onClick={handleSubmit as any}
            disabled={loading}
            className="px-5 py-2 text-[13px] font-semibold bg-[#5433eb] text-white rounded-full hover:bg-[#4325c9] transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Spinner size="sm" /> : <Plus size={14} />}
            {loading ? 'Creating…' : 'Create Product'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Stock Adjust Modal ───────────────────────────────────────────────────────

function AdjustStockModal({ product, warehouses, onClose, onDone }: {
  product: SellerProduct;
  warehouses: SellerWarehouse[];
  onClose: () => void;
  onDone: () => void;
}) {
  const [delta, setDelta] = useState('');
  const [warehouseId, setWarehouseId] = useState(product.warehouse_id ?? warehouses[0]?.id ?? '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const qty = parseInt(delta);
    if (isNaN(qty) || qty === 0) { setError('Enter a non-zero quantity.'); return; }
    try {
      setLoading(true);
      await api.post('/api/sellers/me/inventory/adjust', {
        variant_id: product.variant_id,
        warehouse_id: warehouseId,
        on_hand: qty,
      });
      onDone();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Adjustment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-[24px] w-full max-w-sm shadow-2xl">
        <div className="px-6 py-5 border-b border-[#ebebeb] flex items-center justify-between">
          <h2 className="text-[15px] font-bold tracking-[-0.03em]">Adjust Stock</h2>
          <button onClick={onClose} className="text-[#787574] hover:text-black text-xl leading-none">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <p className="text-[12px] text-[#787574] mb-1">Product</p>
            <p className="text-[13px] font-semibold">{product.product_name} <span className="font-normal text-[#787574]">– {product.variant_name}</span></p>
            <p className="text-[11px] text-[#787574] mt-0.5">Current: <strong>{product.on_hand}</strong> on-hand · <strong>{product.available}</strong> available</p>
          </div>
          <div>
            <label className="block text-[12px] font-semibold text-[#444] mb-1">Quantity Change (+ to add, - to remove)</label>
            <input
              type="number"
              value={delta}
              onChange={e => setDelta(e.target.value)}
              placeholder="e.g. +20 or -5"
              className="w-full px-3 py-2 rounded-[10px] border border-[#ebebeb] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 bg-[#fafafa]"
              required
            />
          </div>
          <div>
            <label className="block text-[12px] font-semibold text-[#444] mb-1">Warehouse</label>
            <select
              value={warehouseId}
              onChange={e => setWarehouseId(e.target.value)}
              className="w-full px-3 py-2 rounded-[10px] border border-[#ebebeb] text-[13px] bg-[#fafafa] outline-none focus:ring-2 focus:ring-[#5433eb]/30"
            >
              {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
            </select>
          </div>
          {error && <p className="text-[12px] text-red-500 bg-red-50 px-3 py-2 rounded-[8px]">{error}</p>}
        </form>
        <div className="px-6 py-4 border-t border-[#ebebeb] flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-[13px] rounded-full border border-[#ebebeb] hover:bg-[#f2f4f5] transition">Cancel</button>
          <button
            onClick={handleSubmit as any}
            disabled={loading}
            className="px-5 py-2 text-[13px] font-semibold bg-[#000] text-white rounded-full hover:bg-[#222] transition disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <Spinner size="sm" /> : null}
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Tab: Overview ────────────────────────────────────────────────────────────

function OverviewTab({ metrics, orders }: { metrics: SellerMetrics | null; orders: SellerOrder[] }) {
  if (!metrics) return <div className="flex justify-center py-16"><Spinner /></div>;

  const recentOrders = [...orders].slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KpiCard
          icon={<DollarSign size={18} />}
          label="Total Revenue"
          value={`₹${metrics.total_sales_display.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
          accent
        />
        <KpiCard icon={<ShoppingBag size={18} />} label="Active Listings" value={metrics.active_listings} />
        <KpiCard icon={<Clock size={18} />}      label="Pending Orders"  value={metrics.pending_orders} />
        <KpiCard icon={<BarChart3 size={18} />}  label="Total Orders"    value={metrics.total_orders} />
        <KpiCard
          icon={<AlertTriangle size={18} />}
          label="Low Stock Items"
          value={metrics.low_stock_items}
          warn={metrics.low_stock_items > 0}
          sub={metrics.low_stock_items > 0 ? '⚠ Alert' : undefined}
        />
        <KpiCard
          icon={<ArrowUpRight size={18} />}
          label="Fulfillment Rate"
          value={metrics.total_orders > 0
            ? `${Math.round(((metrics.total_orders - metrics.pending_orders) / metrics.total_orders) * 100)}%`
            : '—'}
        />
      </div>

      {/* Recent orders stream */}
      <div className="bg-white rounded-[20px] border border-[#ebebeb] overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-[#ebebeb] flex items-center justify-between">
          <h2 className="text-[14px] font-bold tracking-[-0.02em]">Recent Order Activity</h2>
          <span className="text-[11px] text-[#787574]">Last 5 orders</span>
        </div>
        {recentOrders.length === 0 ? (
          <div className="py-12 text-center text-[13px] text-[#787574]">No orders yet. Start selling to see activity here.</div>
        ) : (
          <div className="divide-y divide-[#f2f4f5]">
            {recentOrders.map(o => (
              <div key={o.id} className="px-5 py-3.5 flex items-center justify-between hover:bg-[#fafafa] transition">
                <div>
                  <p className="text-[12px] font-semibold text-[#000]">Order #{o.order_id.slice(0, 8).toUpperCase()}</p>
                  <p className="text-[11px] text-[#787574]">
                    {o.items.length} item(s) · ₹{(o.subtotal / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </p>
                </div>
                <StatusBadge status={o.status} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Tab: Orders ──────────────────────────────────────────────────────────────

function OrdersTab({ orders, onStatusUpdate }: { orders: SellerOrder[]; onStatusUpdate: () => void }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const handleStatusChange = async (orderId: string, newStatus: string) => {
    setUpdatingId(orderId);
    try {
      await api.put(`/api/sellers/me/orders/${orderId}/status`, { status: newStatus });
      onStatusUpdate();
    } catch (err) {
      console.error('Status update failed', err);
    } finally {
      setUpdatingId(null);
    }
  };

  if (orders.length === 0) {
    return (
      <div className="bg-white rounded-[20px] border border-[#ebebeb] py-16 text-center shadow-sm">
        <ShoppingBag size={36} className="mx-auto text-[#ebebeb] mb-3" />
        <p className="text-[14px] font-semibold text-[#787574]">No orders yet</p>
        <p className="text-[12px] text-[#b0b0b0] mt-1">Your customer orders will appear here once you list products.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-[20px] border border-[#ebebeb] overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b border-[#ebebeb]">
        <h2 className="text-[14px] font-bold tracking-[-0.02em]">Order Fulfillment</h2>
        <p className="text-[11px] text-[#787574] mt-0.5">{orders.length} total seller order(s)</p>
      </div>
      <div className="divide-y divide-[#f2f4f5]">
        {orders.map(order => {
          const isExpanded = expandedId === order.id;
          const transitions = VALID_TRANSITIONS[order.status] ?? [];
          const isUpdating = updatingId === order.id;
          return (
            <div key={order.id}>
              <div
                className="px-5 py-4 flex items-center justify-between cursor-pointer hover:bg-[#fafafa] transition"
                onClick={() => setExpandedId(isExpanded ? null : order.id)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  {isExpanded ? <ChevronDown size={16} className="text-[#787574] flex-shrink-0" /> : <ChevronRight size={16} className="text-[#787574] flex-shrink-0" />}
                  <div>
                    <p className="text-[13px] font-semibold">#{order.order_id.slice(0, 8).toUpperCase()}</p>
                    <p className="text-[11px] text-[#787574]">
                      {order.items.length} item(s) · {order.created_at ? new Date(order.created_at).toLocaleDateString('en-IN') : '—'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[13px] font-bold text-[#000]">
                    ₹{(order.subtotal / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </span>
                  <StatusBadge status={order.status} />
                </div>
              </div>

              {isExpanded && (
                <div className="px-5 pb-4 bg-[#fafafa] border-t border-[#f2f4f5]">
                  {/* Line items */}
                  <div className="mt-3 rounded-[12px] border border-[#ebebeb] overflow-hidden bg-white">
                    <table className="w-full text-[12px]">
                      <thead>
                        <tr className="bg-[#f2f4f5] text-[#787574]">
                          <th className="text-left px-3 py-2 font-semibold">Item</th>
                          <th className="text-right px-3 py-2 font-semibold">Price</th>
                          <th className="text-right px-3 py-2 font-semibold">Qty</th>
                          <th className="text-right px-3 py-2 font-semibold">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#f2f4f5]">
                        {order.items.map(item => (
                          <tr key={item.id} className="hover:bg-[#fafafa]">
                            <td className="px-3 py-2 font-medium">{item.snapshot_name}</td>
                            <td className="px-3 py-2 text-right text-[#787574]">₹{(item.snapshot_price / 100).toFixed(2)}</td>
                            <td className="px-3 py-2 text-right">{item.quantity}</td>
                            <td className="px-3 py-2 text-right font-semibold">₹{((item.snapshot_price * item.quantity) / 100).toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Status actions */}
                  {transitions.length > 0 && (
                    <div className="flex items-center gap-2 mt-3">
                      <span className="text-[11px] text-[#787574]">Update status:</span>
                      {transitions.map(s => (
                        <button
                          key={s}
                          onClick={() => handleStatusChange(order.id, s)}
                          disabled={isUpdating}
                          className="px-3 py-1.5 text-[11px] font-semibold rounded-full border border-[#ebebeb] bg-white hover:bg-[#5433eb] hover:text-white hover:border-[#5433eb] transition disabled:opacity-50 flex items-center gap-1"
                        >
                          {isUpdating ? <Spinner size="sm" /> : null}
                          {STATUS_CONFIG[s]?.label ?? s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Tab: Inventory ───────────────────────────────────────────────────────────

function InventoryTab({
  products, warehouses, onRefresh
}: { products: SellerProduct[]; warehouses: SellerWarehouse[]; onRefresh: () => void }) {
  const [adjustTarget, setAdjustTarget] = useState<SellerProduct | null>(null);
  const [showAddProduct, setShowAddProduct] = useState(false);

  const LOW_STOCK_THRESHOLD = 10;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-[14px] font-bold tracking-[-0.02em]">Product Inventory</h2>
          <p className="text-[11px] text-[#787574]">{products.length} listing(s)</p>
        </div>
        <button
          onClick={() => setShowAddProduct(true)}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#5433eb] text-white rounded-full text-[12px] font-semibold hover:bg-[#4325c9] transition shadow-sm"
        >
          <Plus size={14} />
          Add Product
        </button>
      </div>

      {products.length === 0 ? (
        <div className="bg-white rounded-[20px] border border-[#ebebeb] py-16 text-center shadow-sm">
          <Package size={36} className="mx-auto text-[#ebebeb] mb-3" />
          <p className="text-[14px] font-semibold text-[#787574]">No products yet</p>
          <button onClick={() => setShowAddProduct(true)} className="mt-3 px-4 py-2 bg-[#5433eb] text-white rounded-full text-[12px] font-semibold hover:bg-[#4325c9] transition">
            Add your first product
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-[20px] border border-[#ebebeb] overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="bg-[#f2f4f5] text-[#787574]">
                  <th className="text-left px-4 py-3 font-semibold">Product / Variant</th>
                  <th className="text-left px-4 py-3 font-semibold">SKU</th>
                  <th className="text-right px-4 py-3 font-semibold">Price</th>
                  <th className="text-right px-4 py-3 font-semibold">On Hand</th>
                  <th className="text-right px-4 py-3 font-semibold">Reserved</th>
                  <th className="text-right px-4 py-3 font-semibold">Available</th>
                  <th className="text-center px-4 py-3 font-semibold">Status</th>
                  <th className="text-center px-4 py-3 font-semibold">Warehouse</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-[#f2f4f5]">
                {products.map(p => {
                  const isLow = p.available < LOW_STOCK_THRESHOLD;
                  return (
                    <tr key={p.variant_id} className={`hover:bg-[#fafafa] transition ${isLow ? 'bg-red-50/50' : ''}`}>
                      <td className="px-4 py-3">
                        <p className="font-semibold text-[#000]">{p.product_name}</p>
                        <p className="text-[#787574]">{p.variant_name}</p>
                      </td>
                      <td className="px-4 py-3 text-[#787574] font-mono">{p.sku}</td>
                      <td className="px-4 py-3 text-right font-semibold">₹{(p.price / 100).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right">{p.on_hand}</td>
                      <td className="px-4 py-3 text-right text-[#787574]">{p.reserved}</td>
                      <td className="px-4 py-3 text-right">
                        <span className={`font-bold ${isLow ? 'text-red-500' : 'text-emerald-600'}`}>
                          {p.available}
                          {isLow && <span className="ml-1 text-[10px] align-middle">⚠</span>}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${p.is_active ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-gray-100 text-gray-500 border-gray-200'}`}>
                          {p.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center text-[#787574]">{p.warehouse_name ?? '—'}</td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setAdjustTarget(p)}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-semibold rounded-[8px] border border-[#ebebeb] hover:bg-[#5433eb] hover:text-white hover:border-[#5433eb] transition"
                        >
                          <Edit3 size={11} />
                          Adjust
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {adjustTarget && (
        <AdjustStockModal
          product={adjustTarget}
          warehouses={warehouses}
          onClose={() => setAdjustTarget(null)}
          onDone={onRefresh}
        />
      )}
      {showAddProduct && (
        <AddProductModal
          warehouses={warehouses}
          onClose={() => setShowAddProduct(false)}
          onCreated={onRefresh}
        />
      )}
    </div>
  );
}

// ─── Tab: Warehouses ──────────────────────────────────────────────────────────

function WarehousesTab({ warehouses, onCreated }: { warehouses: SellerWarehouse[]; onCreated: () => void }) {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      setLoading(true);
      await api.post('/api/sellers/me/warehouses', { name: name.trim() });
      setName('');
      onCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Failed to create warehouse');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Create warehouse form */}
      <div className="bg-white rounded-[20px] border border-[#ebebeb] p-5 shadow-sm">
        <h3 className="text-[13px] font-bold mb-3">Add New Fulfillment Hub</h3>
        <form onSubmit={handleCreate} className="flex gap-3">
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Warehouse name (e.g. Mumbai North Hub)"
            className="flex-1 px-3 py-2 rounded-[10px] border border-[#ebebeb] text-[13px] outline-none focus:ring-2 focus:ring-[#5433eb]/30 bg-[#fafafa]"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-[#5433eb] text-white rounded-full text-[12px] font-semibold hover:bg-[#4325c9] transition disabled:opacity-50 flex items-center gap-1.5"
          >
            {loading ? <Spinner size="sm" /> : <Plus size={13} />}
            Create
          </button>
        </form>
        {error && <p className="text-[11px] text-red-500 mt-2">{error}</p>}
      </div>

      {/* Warehouse list */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {warehouses.map(w => (
          <div key={w.id} className="bg-white rounded-[16px] border border-[#ebebeb] p-4 shadow-sm hover:shadow-md transition">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-[10px] bg-[#f2f4f5] flex items-center justify-center text-[#5433eb]">
                <Warehouse size={17} />
              </div>
              <div>
                <p className="text-[13px] font-semibold">{w.name}</p>
                <p className="text-[10px] text-[#787574] font-mono">{w.id.slice(0, 8)}&hellip;</p>
              </div>
            </div>
          </div>
        ))}
        {warehouses.length === 0 && (
          <div className="col-span-full text-center py-10 text-[13px] text-[#787574]">
            No warehouses yet. Create your first fulfillment hub above.
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

export const SellerDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [metrics, setMetrics] = useState<SellerMetrics | null>(null);
  const [orders, setOrders] = useState<SellerOrder[]>([]);
  const [products, setProducts] = useState<SellerProduct[]>([]);
  const [warehouses, setWarehouses] = useState<SellerWarehouse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sellerName, setSellerName] = useState('');

  const fetchAll = useCallback(async () => {
    try {
      const [meRes, metricsRes, ordersRes, prodsRes, whRes] = await Promise.all([
        api.get('/api/sellers/me'),
        api.get('/api/sellers/me/metrics'),
        api.get('/api/sellers/me/orders'),
        api.get('/api/sellers/me/products'),
        api.get('/api/sellers/me/warehouses'),
      ]);
      setSellerName(meRes.data.company_name ?? '');
      setMetrics(metricsRes.data);
      setOrders(ordersRes.data);
      setProducts(prodsRes.data);
      setWarehouses(whRes.data);
    } catch (err: any) {
      if (err.response?.status === 403) navigate('/');
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    fetchAll();
  }, [user, fetchAll, navigate]);

  const TABS: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'overview',    label: 'Overview',   icon: <BarChart3 size={15} /> },
    { id: 'orders',      label: 'Orders',     icon: <ShoppingBag size={15} /> },
    { id: 'inventory',   label: 'Inventory',  icon: <Package size={15} /> },
    { id: 'warehouses',  label: 'Warehouses', icon: <Warehouse size={15} /> },
  ];

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <Spinner />
        <p className="text-[13px] text-[#787574] tracking-[-0.017em]">Loading seller portal…</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-7">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-[16px] bg-gradient-to-br from-[#5433eb] to-[#7c5af5] text-white flex items-center justify-center shadow-[0_8px_24px_rgba(84,51,235,0.4)]">
            <Store size={24} />
          </div>
          <div>
            <h1 className="text-[26px] font-bold tracking-[-0.04em] text-[#000]">
              {sellerName || 'Seller Portal'}
            </h1>
            <p className="text-[12px] text-[#787574] mt-0.5">Manage your catalog, inventory, and fulfill orders</p>
          </div>
        </div>
        <button
          onClick={fetchAll}
          className="p-2.5 rounded-[10px] border border-[#ebebeb] text-[#787574] hover:text-[#5433eb] hover:border-[#5433eb]/30 transition"
          title="Refresh dashboard"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {/* Tab bar */}
      <div className="flex items-center gap-1 bg-[#f2f4f5] p-1 rounded-[14px] w-fit">
        {TABS.map(tab => (
          <button
            key={tab.id}
            id={`seller-tab-${tab.id}`}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-[10px] text-[12px] font-semibold transition ${
              activeTab === tab.id
                ? 'bg-white text-[#5433eb] shadow-sm'
                : 'text-[#787574] hover:text-[#000]'
            }`}
          >
            {tab.icon}
            {tab.label}
            {tab.id === 'orders' && metrics && metrics.pending_orders > 0 && (
              <span className="w-4 h-4 bg-red-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center leading-none">
                {metrics.pending_orders}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'overview' && <OverviewTab metrics={metrics} orders={orders} />}
      {activeTab === 'orders' && <OrdersTab orders={orders} onStatusUpdate={fetchAll} />}
      {activeTab === 'inventory' && <InventoryTab products={products} warehouses={warehouses} onRefresh={fetchAll} />}
      {activeTab === 'warehouses' && <WarehousesTab warehouses={warehouses} onCreated={fetchAll} />}
    </div>
  );
};

export default SellerDashboard;
