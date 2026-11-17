import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShoppingBag, ChevronDown, ChevronRight,
  Clock, CheckCircle2, Truck, RefreshCw, XCircle, Package
} from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface OrderItem {
  id: string;
  variant_id: string;
  snapshot_name: string;
  snapshot_price: number;
  quantity: number;
}

interface SellerOrder {
  id: string;
  status: string;
  subtotal: number;
  items: OrderItem[];
}

interface Shipment {
  seller_order_id: string;
  provider: string;
  tracking_number: string;
  status: string;
  estimated_delivery?: string;
}

interface Order {
  id: string;
  status: string;
  payment_status: string;
  total_amount: number;
  created_at: string | null;
  seller_orders: SellerOrder[];
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  PENDING_PAYMENT: { label: 'Pending Payment', color: 'bg-amber-100 text-amber-700 border-amber-200',    icon: <Clock size={12} /> },
  PAID:            { label: 'Paid',            color: 'bg-blue-100 text-blue-700 border-blue-200',       icon: <CheckCircle2 size={12} /> },
  PAYMENT_FAILED:  { label: 'Payment Failed',  color: 'bg-red-100 text-red-700 border-red-200',          icon: <XCircle size={12} /> },
  PROCESSING:      { label: 'Processing',      color: 'bg-purple-100 text-purple-700 border-purple-200', icon: <RefreshCw size={12} /> },
  SHIPPED:         { label: 'Shipped',         color: 'bg-indigo-100 text-indigo-700 border-indigo-200', icon: <Truck size={12} /> },
  DELIVERED:       { label: 'Delivered',       color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: <CheckCircle2 size={12} /> },
  CANCELLED:       { label: 'Cancelled',       color: 'bg-gray-100 text-gray-500 border-gray-200',       icon: <XCircle size={12} /> },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, color: 'bg-gray-100 text-gray-500 border-gray-200', icon: null };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${cfg.color}`}>
      {cfg.icon}{cfg.label}
    </span>
  );
}

export const OrderHistory: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [shipments, setShipments] = useState<Record<string, Shipment[]>>({});
  const [returnMessage, setReturnMessage] = useState<Record<string, string>>({});
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    (async () => {
      try {
        const res = await api.get('/api/orders');
        setOrders(res.data || []);
      } catch (err) {
        console.error('Failed to fetch orders', err);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [user, navigate]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-8 h-8 border-[3px] border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin" />
        <p className="text-[13px] text-[#787574]">Loading your orders…</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[28px] font-bold tracking-[-0.04em] text-[#000]">My Orders</h1>
          <p className="text-[13px] text-[#787574] mt-0.5">
            {orders.length} order{orders.length !== 1 ? 's' : ''} placed
          </p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 border border-[#ebebeb] rounded-full text-[12px] font-semibold text-[#000] hover:bg-[#f2f4f5] transition"
        >
          Continue Shopping
        </button>
      </div>

      {orders.length === 0 ? (
        <div className="bg-white rounded-[28px] border border-[#ebebeb] py-20 text-center shadow-sm space-y-4">
          <ShoppingBag size={40} className="mx-auto text-[#ebebeb]" />
          <h2 className="text-[17px] font-bold text-[#000]">No orders yet</h2>
          <p className="text-[13px] text-[#787574]">Your placed orders will appear here.</p>
          <button
            onClick={() => navigate('/')}
            className="px-5 py-2.5 bg-[#5433eb] text-white rounded-full text-[13px] font-semibold hover:brightness-110 transition shadow-[0_4px_24px_rgba(84,51,235,0.3)]"
          >
            Start Shopping
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const isExpanded = expandedId === order.id;
            const date = order.created_at
              ? new Date(order.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
              : '—';
            const totalItems = order.seller_orders.reduce(
              (s, so) => s + so.items.reduce((ss, i) => ss + i.quantity, 0), 0
            );

            return (
              <div key={order.id} className="bg-white rounded-[24px] border border-[#ebebeb] shadow-sm overflow-hidden">
                {/* Order Header */}
                <div
                  className="px-5 py-4 flex items-center justify-between cursor-pointer hover:bg-[#fafafa] transition"
                  onClick={() => setExpandedId(isExpanded ? null : order.id)}
                >
                  <div className="flex items-center gap-3">
                    {isExpanded
                      ? <ChevronDown size={16} className="text-[#787574]" />
                      : <ChevronRight size={16} className="text-[#787574]" />}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[13px] font-bold text-[#000]">
                          #{order.id.slice(0, 8).toUpperCase()}
                        </span>
                        <StatusBadge status={order.status} />
                      </div>
                      <p className="text-[11px] text-[#787574] mt-0.5">
                        {date} · {totalItems} item{totalItems !== 1 ? 's' : ''}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-[14px] font-bold text-[#000]">
                      ₹{(order.total_amount / 100).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </p>
                    <StatusBadge status={order.payment_status} />
                  </div>
                </div>

                {/* Expanded: Seller Orders + Items */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-[#f2f4f5] pt-4 space-y-4">
                    <button
                      onClick={async () => {
                        const response = await api.get(`/api/v1/shipping/orders/${order.id}`);
                        setShipments((current) => ({ ...current, [order.id]: response.data || [] }));
                      }}
                      className="inline-flex items-center gap-2 px-3 py-2 rounded-full border border-[#ebebeb] text-[11px] font-semibold text-[#5433eb] hover:bg-[#f5f3ff]"
                    >
                      <Truck size={13} /> Load tracking
                    </button>
                    {shipments[order.id]?.map((shipment) => (
                      <div key={shipment.tracking_number} className="rounded-[14px] bg-[#f5f3ff] border border-[#e6e0ff] px-4 py-3 text-[12px]">
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-semibold text-[#000]">{shipment.status}</span>
                          <span className="font-mono text-[#5433eb]">{shipment.tracking_number}</span>
                        </div>
                        <p className="text-[11px] text-[#787574] mt-1">MOCK DEMONSTRATION · Estimated delivery {shipment.estimated_delivery ? new Date(shipment.estimated_delivery).toLocaleDateString('en-IN') : 'pending'}</p>
                      </div>
                    ))}
                    {order.seller_orders.length === 0 ? (
                      <p className="text-[12px] text-[#787574]">No items found.</p>
                    ) : (
                      order.seller_orders.map((so) => (
                        <div key={so.id} className="rounded-[16px] border border-[#ebebeb] overflow-hidden">
                          {/* Seller sub-order header */}
                          <div className="px-4 py-2.5 bg-[#f2f4f5] flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Package size={13} className="text-[#787574]" />
                              <span className="text-[11px] font-semibold text-[#787574]">
                                Shipment #{so.id.slice(0, 6).toUpperCase()}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <StatusBadge status={so.status} />
                              {(so.status === 'SHIPPED' || so.status === 'DELIVERED') && (
                                <button
                                  onClick={async (event) => {
                                    event.stopPropagation();
                                    const response = await api.post(`/api/v1/returns/seller-orders/${so.id}`, { reason: 'Customer requested return' });
                                    setReturnMessage((current) => ({ ...current, [so.id]: `Return ${response.data.status.toLowerCase()}` }));
                                  }}
                                  className="px-2.5 py-1 rounded-full border border-[#ebebeb] bg-white text-[10px] font-semibold text-[#5433eb] hover:bg-[#f5f3ff]"
                                >
                                  Request return
                                </button>
                              )}
                            </div>
                          </div>
                          {returnMessage[so.id] && <p className="px-4 py-2 text-[11px] text-[#5433eb]">{returnMessage[so.id]}</p>}

                          {/* Items table */}
                          <table className="w-full text-[12px]">
                            <tbody className="divide-y divide-[#f2f4f5]">
                              {so.items.map((item) => (
                                <tr key={item.id} className="hover:bg-[#fafafa]">
                                  <td className="px-4 py-3 font-medium text-[#000]">{item.snapshot_name}</td>
                                  <td className="px-4 py-3 text-center text-[#787574]">×{item.quantity}</td>
                                  <td className="px-4 py-3 text-right font-semibold text-[#000]">
                                    ₹{((item.snapshot_price * item.quantity) / 100).toFixed(2)}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                            <tfoot>
                              <tr className="bg-[#f2f4f5]">
                                <td className="px-4 py-2 text-[11px] font-semibold text-[#787574]" colSpan={2}>
                                  Shipment subtotal
                                </td>
                                <td className="px-4 py-2 text-right text-[12px] font-bold text-[#000]">
                                  ₹{(so.subtotal / 100).toFixed(2)}
                                </td>
                              </tr>
                            </tfoot>
                          </table>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
export default OrderHistory;
