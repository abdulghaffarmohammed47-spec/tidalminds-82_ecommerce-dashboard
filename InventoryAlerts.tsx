import { AlertOctagon, AlertTriangle, ArrowRight } from "lucide-react";
import type { Product } from "../../data/mockData";

export default function InventoryAlerts({
  products,
  onGoToProducts,
}: {
  products: Product[];
  onGoToProducts: () => void;
}) {
  const outOfStock = products.filter((p) => p.stock === 0);
  const lowStock = products.filter((p) => p.stock > 0 && p.stock <= 10);

  return (
    <div className="flex h-full flex-col space-y-3">
      {outOfStock.length > 0 && (
        <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-3.5 dark:border-red-500/25 dark:bg-red-500/10">
          <AlertOctagon className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
          <div className="min-w-0">
            <p className="text-sm font-bold text-red-700 dark:text-red-400">
              {outOfStock.length} product(s) out of stock
            </p>
            <p className="mt-0.5 line-clamp-2 text-xs text-red-600/80 dark:text-red-400/70">
              {outOfStock.map((p) => p.name).join(", ")}
            </p>
          </div>
        </div>
      )}

      {lowStock.length > 0 && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-3.5 dark:border-amber-500/25 dark:bg-amber-500/10">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />
          <div className="min-w-0">
            <p className="text-sm font-bold text-amber-700 dark:text-amber-400">
              {lowStock.length} product(s) running low
            </p>
            <p className="mt-0.5 line-clamp-3 text-xs text-amber-600/80 dark:text-amber-400/70">
              {lowStock.map((p) => `${p.name} (${p.stock} left)`).join(", ")}
            </p>
          </div>
        </div>
      )}

      {outOfStock.length === 0 && lowStock.length === 0 && (
        <div className="flex flex-1 items-center justify-center rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center dark:border-emerald-500/25 dark:bg-emerald-500/10">
          <div>
            <p className="text-2xl">✅</p>
            <p className="mt-1 text-sm font-bold text-emerald-700 dark:text-emerald-400">
              Inventory healthy
            </p>
            <p className="text-xs text-emerald-600/80 dark:text-emerald-400/70">
              All products are sufficiently stocked.
            </p>
          </div>
        </div>
      )}

      <button
        onClick={onGoToProducts}
        className="inline-flex items-center gap-1 self-start text-xs font-semibold text-indigo-600 transition hover:text-indigo-500 dark:text-indigo-400"
      >
        Manage inventory <ArrowRight className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
