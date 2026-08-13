import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { money, type Order, type OrderStatus } from "../../data/mockData";
import { cn } from "../../utils/cn";
import { CSVExportBtn } from "../shared/ui";

const STATUSES: OrderStatus[] = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"];

const STATUS_SELECT_CLS: Record<OrderStatus, string> = {
  Pending: "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400",
  Processing: "bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-400",
  Shipped: "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-400",
  Delivered: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400",
  Cancelled: "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400",
};

export default function OrdersPage({
  orders,
  setOrders,
}: {
  orders: Order[];
  setOrders: React.Dispatch<React.SetStateAction<Order[]>>;
}) {
  const [filter, setFilter] = useState<OrderStatus | "All">("All");
  const [search, setSearch] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const counts = useMemo(() => {
    const c: Record<string, number> = { All: orders.length };
    for (const s of STATUSES) c[s] = orders.filter((o) => o.status === s).length;
    return c;
  }, [orders]);

  const filtered = useMemo(
    () =>
      orders.filter((o) => {
        const matchStatus = filter === "All" || o.status === filter;
        const q = search.toLowerCase();
        const matchSearch =
          o.customer.toLowerCase().includes(q) ||
          o.id.toLowerCase().includes(q) ||
          o.product.toLowerCase().includes(q);
        const matchDate = (!dateFrom || o.date >= dateFrom) && (!dateTo || o.date <= dateTo);
        return matchStatus && matchSearch && matchDate;
      }),
    [orders, filter, search, dateFrom, dateTo]
  );

  const updateStatus = (id: string, status: OrderStatus) => {
    setOrders((prev) => prev.map((o) => (o.id === id ? { ...o, status } : o)));
  };

  const grossRevenue = filtered.filter((o) => o.status !== "Cancelled").reduce((s, o) => s + o.amount, 0);
  const avgOrder = filtered.length ? grossRevenue / Math.max(1, filtered.filter((o) => o.status !== "Cancelled").length) : 0;

  const exportRows = filtered.map((o) => ({
    id: o.id,
    customer: o.customer,
    email: o.email,
    product: o.product,
    amount: o.amount,
    status: o.status,
    date: o.date,
    items: o.items,
  }));

  return (
    <div className="animate-fade-up space-y-5">
      {/* Mini stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: "Filtered orders", value: filtered.length.toLocaleString(), tone: "text-indigo-600 dark:text-indigo-400" },
          { label: "Gross revenue (excl. cancelled)", value: money(grossRevenue), tone: "text-emerald-600 dark:text-emerald-400" },
          { label: "Average order value", value: money(avgOrder), tone: "text-amber-600 dark:text-amber-400" },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{s.label}</p>
            <p className={cn("mt-1 text-xl font-bold", s.tone)}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Card */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {/* Toolbar */}
        <div className="space-y-3 border-b border-slate-100 p-4 dark:border-slate-800">
          {/* Status pills */}
          <div className="flex flex-wrap gap-2">
            {(["All", ...STATUSES] as const).map((s) => (
              <button
                key={s}
                onClick={() => setFilter(s)}
                className={cn(
                  "rounded-full px-3.5 py-1.5 text-xs font-semibold transition",
                  filter === s
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                )}
              >
                {s}
                <span
                  className={cn(
                    "ml-1.5 rounded-full px-1.5 py-0.5 text-[10px] font-bold",
                    filter === s ? "bg-white/25" : "bg-slate-200 dark:bg-slate-700"
                  )}
                >
                  {counts[s]}
                </span>
              </button>
            ))}
          </div>

          {/* Search + date range + export */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-52 flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                placeholder="Search by order ID, customer or product…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:bg-slate-800"
              />
            </div>
            <label className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
              From
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 outline-none focus:border-indigo-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:[color-scheme:dark]"
              />
            </label>
            <label className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
              To
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 outline-none focus:border-indigo-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:[color-scheme:dark]"
              />
            </label>
            {(dateFrom || dateTo) && (
              <button
                onClick={() => {
                  setDateFrom("");
                  setDateTo("");
                }}
                className="text-xs font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
              >
                Clear
              </button>
            )}
            <CSVExportBtn data={exportRows} filename="orders.csv" label="Export" />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-left text-xs font-semibold uppercase tracking-wide text-slate-400 dark:border-slate-800 dark:bg-slate-800/40 dark:text-slate-500">
                <th className="px-5 py-3">Order</th>
                <th className="px-3 py-3">Customer</th>
                <th className="px-3 py-3">Product</th>
                <th className="px-3 py-3">Date</th>
                <th className="px-3 py-3">Items</th>
                <th className="px-3 py-3">Amount</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((o) => (
                <tr
                  key={o.id}
                  className="border-b border-slate-50 transition hover:bg-slate-50/70 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
                >
                  <td className="px-5 py-3 font-semibold text-indigo-600 dark:text-indigo-400">
                    {o.id}
                  </td>
                  <td className="px-3 py-3">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{o.customer}</p>
                    <p className="text-xs text-slate-400">{o.email}</p>
                  </td>
                  <td className="px-3 py-3 text-slate-600 dark:text-slate-300">{o.product}</td>
                  <td className="px-3 py-3 text-slate-500 dark:text-slate-400">{o.date}</td>
                  <td className="px-3 py-3 text-slate-500 dark:text-slate-400">{o.items}</td>
                  <td className="px-3 py-3 font-semibold text-slate-800 dark:text-slate-200">
                    {money(o.amount)}
                  </td>
                  <td className="px-5 py-3">
                    <select
                      value={o.status}
                      onChange={(e) => updateStatus(o.id, e.target.value as OrderStatus)}
                      className={cn(
                        "cursor-pointer appearance-none rounded-full border-none px-3 py-1.5 pr-7 text-xs font-semibold outline-none transition focus:ring-2 focus:ring-indigo-500/40",
                        STATUS_SELECT_CLS[o.status]
                      )}
                      aria-label={`Update status for ${o.id}`}
                      style={{
                        backgroundImage:
                          "url(\"data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='none'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%2364748b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\")",
                        backgroundRepeat: "no-repeat",
                        backgroundPosition: "right 0.6rem center",
                      }}
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-sm text-slate-400">
                    No orders match the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-400 dark:border-slate-800">
          Showing {filtered.length} of {orders.length} orders · status changes apply instantly
        </div>
      </div>
    </div>
  );
}
