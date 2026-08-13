import type { Product } from "../../data/mockData";
import { money } from "../../data/mockData";

export default function TopProducts({ products }: { products: Product[] }) {
  const top = [...products].sort((a, b) => b.sold - a.sold).slice(0, 5);
  const max = top[0]?.sold ?? 1;

  return (
    <div className="space-y-3.5">
      {top.map((p, i) => (
        <div key={p.id} className="flex items-center gap-3">
          <span className="w-4 text-center text-xs font-bold text-slate-400 dark:text-slate-500">
            {i + 1}
          </span>
          <div
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br text-base ${p.tile}`}
          >
            {p.emoji}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-baseline justify-between gap-2">
              <p className="truncate text-sm font-semibold text-slate-800 dark:text-slate-200">
                {p.name}
              </p>
              <p className="shrink-0 text-xs font-semibold text-slate-500 dark:text-slate-400">
                {money(p.sold * p.price)}
              </p>
            </div>
            <div className="mt-1.5 flex items-center gap-2">
              <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                  style={{ width: `${(p.sold / max) * 100}%` }}
                />
              </div>
              <span className="w-14 text-right text-[11px] font-medium text-slate-400">
                {p.sold} sold
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
