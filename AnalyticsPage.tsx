import { useMemo, useState } from "react";
import { CalendarRange, RotateCcw } from "lucide-react";
import {
  categoryRevenue,
  dailyRevenue,
  monthlyRevenue,
  money,
  type MonthlyPoint,
  type Product,
} from "../../data/mockData";
import { useTheme } from "../../context/ThemeContext";
import { cn } from "../../utils/cn";
import { CSVExportBtn, WidgetCard } from "../shared/ui";
import RevenueChart, { type ChartType } from "../charts/RevenueChart";
import OrdersChart from "../charts/OrdersChart";
import TopProducts from "../dashboard/TopProducts";

export default function AnalyticsPage({ products }: { products: Product[] }) {
  const { dark } = useTheme();
  const [draftFrom, setDraftFrom] = useState("2025-10-01");
  const [draftTo, setDraftTo] = useState("2026-09-30");
  const [from, setFrom] = useState("2025-10-01");
  const [to, setTo] = useState("2026-09-30");
  const [chartType, setChartType] = useState<ChartType>("line");
  const [selectedPoint, setSelectedPoint] = useState<MonthlyPoint | null>(null);

  const filtered = useMemo(
    () => monthlyRevenue.filter((m) => m.date >= from && m.date <= to),
    [from, to]
  );

  const totals = useMemo(() => {
    const revenue = filtered.reduce((s, m) => s + m.revenue, 0);
    const orders = filtered.reduce((s, m) => s + m.orders, 0);
    return { revenue, orders, avg: filtered.length ? revenue / filtered.length : 0 };
  }, [filtered]);

  const dateInputCls =
    "rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 outline-none transition focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:[color-scheme:dark]";

  const exportRows = filtered.map((m) => ({
    month: m.month,
    revenue: m.revenue,
    orders: m.orders,
    customers: m.customers,
    avgOrderValue: Number((m.revenue / m.orders).toFixed(2)),
  }));

  return (
    <div className="animate-fade-up space-y-5">
      {/* Date range controls */}
      <div className="flex flex-wrap items-end gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div>
          <label className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            <CalendarRange className="h-3.5 w-3.5" /> Date range
          </label>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <input type="date" value={draftFrom} onChange={(e) => setDraftFrom(e.target.value)} className={dateInputCls} />
            <span className="text-slate-400">→</span>
            <input type="date" value={draftTo} onChange={(e) => setDraftTo(e.target.value)} className={dateInputCls} />
            <button
              onClick={() => {
                setFrom(draftFrom);
                setTo(draftTo);
                setSelectedPoint(null);
              }}
              className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-500"
            >
              Apply
            </button>
            <button
              onClick={() => {
                setDraftFrom("2025-10-01");
                setDraftTo("2026-09-30");
                setFrom("2025-10-01");
                setTo("2026-09-30");
                setSelectedPoint(null);
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-3.5 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </button>
          </div>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <CSVExportBtn data={exportRows} filename="revenue-analytics.csv" label="Export report" />
        </div>
      </div>

      {/* Range summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: `Revenue (${filtered.length} mo)`, value: money(totals.revenue), tone: "text-emerald-600 dark:text-emerald-400" },
          { label: "Orders", value: totals.orders.toLocaleString(), tone: "text-indigo-600 dark:text-indigo-400" },
          { label: "Avg revenue / month", value: money(totals.avg), tone: "text-amber-600 dark:text-amber-400" },
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

      {/* Main chart */}
      <WidgetCard
        title="Revenue Trend"
        subtitle={filtered.length ? `${filtered[0].month} — ${filtered[filtered.length - 1].month} · click a data point for details` : "No data in range"}
        action={
          <div className="flex rounded-lg bg-slate-100 p-0.5 dark:bg-slate-800">
            {(["line", "area", "bar"] as ChartType[]).map((t) => (
              <button
                key={t}
                onClick={() => setChartType(t)}
                className={cn(
                  "rounded-md px-2.5 py-1 text-xs font-semibold capitalize transition",
                  chartType === t
                    ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-indigo-300"
                    : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                {t}
              </button>
            ))}
          </div>
        }
      >
        {filtered.length === 0 ? (
          <div className="flex h-64 items-center justify-center text-sm text-slate-400">
            No data in the selected range. Try widening the dates.
          </div>
        ) : (
          <>
            <RevenueChart
              labels={filtered.map((m) => m.month)}
              values={filtered.map((m) => m.revenue)}
              dark={dark}
              type={chartType}
              height={300}
              onPointClick={(i) => setSelectedPoint(filtered[i])}
            />
            {selectedPoint && (
              <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 rounded-xl bg-indigo-50 px-4 py-3 text-sm dark:bg-indigo-500/10">
                <span className="font-bold text-indigo-700 dark:text-indigo-300">
                  {selectedPoint.month}
                </span>
                <span className="text-slate-600 dark:text-slate-300">
                  Revenue <b className="text-emerald-600 dark:text-emerald-400">{money(selectedPoint.revenue)}</b>
                </span>
                <span className="text-slate-600 dark:text-slate-300">
                  Orders <b>{selectedPoint.orders}</b>
                </span>
                <span className="text-slate-600 dark:text-slate-300">
                  New customers <b>{selectedPoint.customers}</b>
                </span>
                <span className="text-slate-600 dark:text-slate-300">
                  Avg order <b>{money(selectedPoint.revenue / selectedPoint.orders)}</b>
                </span>
              </div>
            )}
          </>
        )}
      </WidgetCard>

      {/* Secondary charts */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <WidgetCard title="Sales by Category" subtitle="Share of total revenue">
          <OrdersChart
            labels={categoryRevenue.map((c) => c.category)}
            values={categoryRevenue.map((c) => c.value)}
            dark={dark}
            centerLabel="Total"
            centerValue="100%"
          />
        </WidgetCard>
        <WidgetCard title="Daily Revenue (this week)" subtitle="Gross sales per weekday">
          <RevenueChart
            labels={dailyRevenue.map((d) => d.day)}
            values={dailyRevenue.map((d) => d.revenue)}
            dark={dark}
            type="bar"
            height={256}
          />
        </WidgetCard>
      </div>

      {/* Top products */}
      <WidgetCard title="Top Selling Products" subtitle="Ranked by units sold across the catalog">
        <TopProducts products={products} />
      </WidgetCard>
    </div>
  );
}
