import { useMemo, useState } from "react";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  rectSortingStrategy,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { DollarSign, Package, ShoppingCart, Users } from "lucide-react";
import {
  categoryRevenue,
  dailyRevenue,
  monthlyRevenue,
  money,
  type MonthlyPoint,
  type Order,
  type Product,
} from "../../data/mockData";
import { useTheme } from "../../context/ThemeContext";
import { cn } from "../../utils/cn";
import { DragHandle, StatCard, WidgetCard } from "../shared/ui";
import RevenueChart, { type ChartType } from "../charts/RevenueChart";
import OrdersChart from "../charts/OrdersChart";
import RecentOrders from "./RecentOrders";
import InventoryAlerts from "./InventoryAlerts";
import TopProducts from "./TopProducts";

type WidgetId =
  | "revenue"
  | "category"
  | "daily"
  | "recent-orders"
  | "alerts"
  | "top-products";

const WIDGET_ORDER: WidgetId[] = [
  "revenue",
  "category",
  "daily",
  "recent-orders",
  "alerts",
  "top-products",
];

const SPANS: Record<WidgetId, string> = {
  revenue: "lg:col-span-2",
  category: "",
  daily: "",
  "recent-orders": "lg:col-span-2",
  alerts: "",
  "top-products": "",
};

// ─── Sortable wrapper ─────────────────────────────────────────────────────
function SortableWidget({
  id,
  span,
  children,
}: {
  id: WidgetId;
  span?: string;
  children: (handle: React.ReactNode) => React.ReactNode;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id });

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={cn(span, isDragging && "z-40 opacity-95 drop-shadow-2xl")}
    >
      {children(
        <DragHandle listeners={listeners} attributes={attributes} />
      )}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────
export default function DashboardPage({
  products,
  orders,
  onNavigate,
}: {
  products: Product[];
  orders: Order[];
  onNavigate: (page: "products" | "orders") => void;
}) {
  const { dark } = useTheme();
  const [widgets, setWidgets] = useState<WidgetId[]>(WIDGET_ORDER);
  const [chartType, setChartType] = useState<ChartType>("area");
  const [selectedMonth, setSelectedMonth] = useState<MonthlyPoint | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setWidgets((prev) =>
        arrayMove(prev, prev.indexOf(active.id as WidgetId), prev.indexOf(over.id as WidgetId))
      );
    }
  };

  const totalRevenue = monthlyRevenue.reduce((s, m) => s + m.revenue, 0);
  const totalOrders = monthlyRevenue.reduce((s, m) => s + m.orders, 0);
  const totalCustomers = 3421; // all-time registered
  const lowStockCount = products.filter((p) => p.stock <= 10).length;

  const recentOrders = useMemo(
    () => [...orders].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 6),
    [orders]
  );

  const renderWidget = (id: WidgetId, handle: React.ReactNode): React.ReactNode => {
    switch (id) {
      case "revenue":
        return (
          <WidgetCard
            handle={handle}
            title="Monthly Revenue"
            subtitle="Click any data point to drill down into that month"
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
            <RevenueChart
              labels={monthlyRevenue.map((m) => m.month)}
              values={monthlyRevenue.map((m) => m.revenue)}
              dark={dark}
              type={chartType}
              onPointClick={(i) => setSelectedMonth(monthlyRevenue[i])}
            />
            {selectedMonth && (
              <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
                {[
                  { label: "Revenue", value: money(selectedMonth.revenue) },
                  { label: "Orders", value: selectedMonth.orders.toLocaleString() },
                  { label: "New customers", value: selectedMonth.customers.toLocaleString() },
                  {
                    label: "Avg order value",
                    value: money(selectedMonth.revenue / selectedMonth.orders),
                  },
                ].map((s) => (
                  <div
                    key={s.label}
                    className="rounded-xl bg-indigo-50 px-3 py-2.5 dark:bg-indigo-500/10"
                  >
                    <p className="text-[11px] font-medium text-indigo-500 dark:text-indigo-400">
                      {selectedMonth.month} · {s.label}
                    </p>
                    <p className="mt-0.5 text-sm font-bold text-slate-900 dark:text-white">
                      {s.value}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </WidgetCard>
        );

      case "category":
        return (
          <WidgetCard
            handle={handle}
            title="Sales by Category"
            subtitle={selectedCategory != null ? `Showing: ${categoryRevenue[selectedCategory].category}` : "Click a segment to filter"}
          >
            <OrdersChart
              labels={categoryRevenue.map((c) => c.category)}
              values={categoryRevenue.map((c) => c.value)}
              dark={dark}
              centerLabel="Share"
              centerValue={selectedCategory != null ? `${categoryRevenue[selectedCategory].value}%` : "100%"}
              onSliceClick={(i) =>
                setSelectedCategory(selectedCategory === i ? null : i)
              }
            />
          </WidgetCard>
        );

      case "daily":
        return (
          <WidgetCard
            handle={handle}
            title="This Week's Revenue"
            subtitle="Daily gross sales, Mon–Sun"
          >
            <RevenueChart
              labels={dailyRevenue.map((d) => d.day)}
              values={dailyRevenue.map((d) => d.revenue)}
              dark={dark}
              type="bar"
              height={232}
            />
          </WidgetCard>
        );

      case "recent-orders":
        return (
          <WidgetCard
            handle={handle}
            title="Recent Orders"
            subtitle={`Latest ${recentOrders.length} of ${orders.length} tracked orders`}
          >
            <RecentOrders orders={recentOrders} onViewAll={() => onNavigate("orders")} />
          </WidgetCard>
        );

      case "alerts":
        return (
          <WidgetCard
            handle={handle}
            title="Inventory Alerts"
            subtitle={`${lowStockCount} item(s) need attention`}
          >
            <InventoryAlerts products={products} onGoToProducts={() => onNavigate("products")} />
          </WidgetCard>
        );

      case "top-products":
        return (
          <WidgetCard handle={handle} title="Top Products" subtitle="Best sellers by units sold">
            <TopProducts products={products} />
          </WidgetCard>
        );
    }
  };

  return (
    <div className="animate-fade-up space-y-5">
      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Total Revenue"
          value={money(totalRevenue)}
          change="+12.5%"
          trend="up"
          icon={DollarSign}
          iconClasses="from-emerald-500 to-teal-600"
          spark={monthlyRevenue.map((m) => m.revenue)}
        />
        <StatCard
          title="Total Orders"
          value={totalOrders.toLocaleString()}
          change="+8.2%"
          trend="up"
          icon={ShoppingCart}
          iconClasses="from-indigo-500 to-violet-600"
          spark={monthlyRevenue.map((m) => m.orders)}
        />
        <StatCard
          title="Total Customers"
          value={totalCustomers.toLocaleString()}
          change="+5.1%"
          trend="up"
          icon={Users}
          iconClasses="from-sky-500 to-blue-600"
          spark={monthlyRevenue.map((m) => m.customers)}
        />
        <StatCard
          title="Active Products"
          value={products.length.toString()}
          change="-2.3%"
          trend="down"
          icon={Package}
          iconClasses="from-orange-400 to-rose-500"
        />
      </div>

      <p className="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500">
        <span className="inline-block h-1.5 w-1.5 rounded-full bg-indigo-400" />
        Drag the ⠿ handle on any widget to rearrange your dashboard
      </p>

      {/* Draggable widget grid */}
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={widgets} strategy={rectSortingStrategy}>
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            {widgets.map((id) => (
              <SortableWidget key={id} id={id} span={SPANS[id]}>
                {(handle) => renderWidget(id, handle)}
              </SortableWidget>
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}
