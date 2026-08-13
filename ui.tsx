import { Download, GripVertical, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "../../utils/cn";
import { exportToCSV } from "../../utils/csvExport";

// ─── Status badge ─────────────────────────────────────────────────────────
const STATUS_STYLES: Record<string, string> = {
  Pending: "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400",
  Processing: "bg-blue-100 text-blue-700 dark:bg-blue-500/15 dark:text-blue-400",
  Shipped: "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-400",
  Delivered: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400",
  Cancelled: "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400",
  "In Stock": "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400",
  "Low Stock": "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400",
  "Out of Stock": "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400",
  Active: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400",
  Inactive: "bg-slate-200 text-slate-600 dark:bg-slate-500/20 dark:text-slate-400",
};

const STATUS_DOTS: Record<string, string> = {
  Pending: "bg-amber-500",
  Processing: "bg-blue-500",
  Shipped: "bg-indigo-500",
  Delivered: "bg-emerald-500",
  Cancelled: "bg-red-500",
  "In Stock": "bg-emerald-500",
  "Low Stock": "bg-amber-500",
  "Out of Stock": "bg-red-500",
  Active: "bg-emerald-500",
  Inactive: "bg-slate-400",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold whitespace-nowrap",
        STATUS_STYLES[status] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", STATUS_DOTS[status] ?? "bg-slate-400")} />
      {status}
    </span>
  );
}

// ─── CSV export button ────────────────────────────────────────────────────
export function CSVExportBtn({
  data,
  filename,
  label = "Export CSV",
  className,
}: {
  data: Record<string, unknown>[];
  filename: string;
  label?: string;
  className?: string;
}) {
  return (
    <button
      onClick={() => exportToCSV(data, filename)}
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700",
        className
      )}
    >
      <Download className="h-4 w-4" />
      {label}
    </button>
  );
}

// ─── Dashboard widget card ────────────────────────────────────────────────
export function WidgetCard({
  title,
  subtitle,
  action,
  handle,
  children,
  className,
  bodyClassName,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  handle?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900",
        className
      )}
    >
      <div className="flex items-start justify-between gap-3 px-5 pt-4 pb-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
          {subtitle && (
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{subtitle}</p>
          )}
        </div>
        <div className="flex items-center gap-1">
          {action}
          {handle}
        </div>
      </div>
      <div className={cn("flex-1 px-5 pb-5", bodyClassName)}>{children}</div>
    </div>
  );
}

export function DragHandle({
  listeners,
  attributes,
  className,
}: {
  listeners?: object;
  attributes?: object;
  className?: string;
}) {
  return (
    <button
      {...listeners}
      {...attributes}
      aria-label="Drag to reorder"
      className={cn(
        "touch-none cursor-grab rounded-md p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 active:cursor-grabbing dark:hover:bg-slate-800 dark:hover:text-slate-300",
        className
      )}
    >
      <GripVertical className="h-4 w-4" />
    </button>
  );
}

// ─── Stat card (KPI) ──────────────────────────────────────────────────────
export function StatCard({
  title,
  value,
  change,
  trend,
  icon: Icon,
  iconClasses,
  spark,
}: {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: LucideIcon;
  iconClasses: string;
  spark?: number[];
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="mt-1.5 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            {value}
          </p>
          <p
            className={cn(
              "mt-2 flex items-center gap-1 text-xs font-semibold",
              trend === "up" ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"
            )}
          >
            <span>{trend === "up" ? "↑" : "↓"}</span>
            {change}
            <span className="font-normal text-slate-400 dark:text-slate-500">vs last month</span>
          </p>
        </div>
        <div
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-sm",
            iconClasses
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {spark && (
        <div className="mt-3">
          <Sparkline points={spark} trend={trend} />
        </div>
      )}
    </div>
  );
}

function Sparkline({ points, trend }: { points: number[]; trend: "up" | "down" }) {
  const w = 200;
  const h = 36;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const step = w / (points.length - 1);
  const coords = points.map((p, i) => `${(i * step).toFixed(1)},${(h - 4 - ((p - min) / range) * (h - 8)).toFixed(1)}`);
  const color = trend === "up" ? "#10b981" : "#ef4444";
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="h-9 w-full" preserveAspectRatio="none">
      <polyline
        points={coords.join(" ")}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        cx={w}
        cy={h - 4 - ((points[points.length - 1] - min) / range) * (h - 8)}
        r="2.5"
        fill={color}
      />
    </svg>
  );
}

// ─── Toggle switch (settings) ─────────────────────────────────────────────
export function ToggleSwitch({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label?: string;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors",
        checked ? "bg-indigo-600" : "bg-slate-300 dark:bg-slate-600"
      )}
    >
      <span
        className={cn(
          "inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform",
          checked ? "translate-x-6" : "translate-x-1"
        )}
      />
    </button>
  );
}
