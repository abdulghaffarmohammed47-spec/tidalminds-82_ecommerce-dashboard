import {
  BarChart3,
  LayoutDashboard,
  Package,
  Settings,
  ShoppingCart,
  Store,
  Users,
  X,
  Zap,
} from "lucide-react";
import { cn } from "../../utils/cn";
import type { Page } from "../../types";

const NAV_ITEMS: { key: Page; label: string; icon: typeof LayoutDashboard }[] = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "products", label: "Products", icon: Package },
  { key: "orders", label: "Orders", icon: ShoppingCart },
  { key: "customers", label: "Customers", icon: Users },
  { key: "analytics", label: "Analytics", icon: BarChart3 },
  { key: "settings", label: "Settings", icon: Settings },
];

export default function Sidebar({
  page,
  onNavigate,
  open,
  onClose,
  pendingCount,
  lowStockCount,
}: {
  page: Page;
  onNavigate: (p: Page) => void;
  open: boolean;
  onClose: () => void;
  pendingCount: number;
  lowStockCount: number;
}) {
  const badgeFor = (key: Page): number | null => {
    if (key === "orders") return pendingCount || null;
    if (key === "products") return lowStockCount || null;
    return null;
  };

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-300 dark:border-slate-800 dark:bg-slate-900",
          open ? "translate-x-0" : "-translate-x-full",
          "lg:translate-x-0"
        )}
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-500/30">
              <Store className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
                Admin<span className="text-indigo-600 dark:text-indigo-400">Pro</span>
              </h1>
              <p className="text-[11px] font-medium text-slate-400 dark:text-slate-500">
                E-commerce Suite v2.4
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 lg:hidden dark:hover:bg-slate-800"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-2">
          <p className="px-3 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
            Menu
          </p>
          {NAV_ITEMS.map((item) => {
            const active = page === item.key;
            const badge = badgeFor(item.key);
            return (
              <button
                key={item.key}
                onClick={() => onNavigate(item.key)}
                className={cn(
                  "group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                  active
                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
                )}
              >
                <item.icon
                  className={cn(
                    "h-[18px] w-[18px]",
                    active
                      ? "text-white"
                      : "text-slate-400 group-hover:text-slate-600 dark:text-slate-500 dark:group-hover:text-slate-300"
                  )}
                />
                <span className="flex-1 text-left">{item.label}</span>
                {badge != null && (
                  <span
                    className={cn(
                      "rounded-full px-2 py-0.5 text-[10px] font-bold",
                      active
                        ? "bg-white/20 text-white"
                        : "bg-red-100 text-red-600 dark:bg-red-500/15 dark:text-red-400"
                    )}
                  >
                    {badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom card */}
        <div className="p-4">
          <div className="rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-500 to-violet-600 p-4 text-white shadow-lg shadow-indigo-500/25">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-300" />
              <p className="text-sm font-bold">Pro Plan</p>
            </div>
            <p className="mt-1 text-xs text-indigo-100">
              Advanced analytics & unlimited exports unlocked.
            </p>
            <button className="mt-3 w-full rounded-lg bg-white/15 py-1.5 text-xs font-semibold backdrop-blur transition hover:bg-white/25">
              Upgrade account
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
