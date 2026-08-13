import type { Order } from "../../data/mockData";
import { money } from "../../data/mockData";
import { StatusBadge } from "../shared/ui";

export default function RecentOrders({
  orders,
  onViewAll,
}: {
  orders: Order[];
  onViewAll: () => void;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="-mx-5 flex-1 overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="text-left text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
              <th className="px-5 py-2.5">Order</th>
              <th className="px-3 py-2.5">Customer</th>
              <th className="px-3 py-2.5">Amount</th>
              <th className="px-3 py-2.5">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr
                key={o.id}
                className="border-t border-slate-100 transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
              >
                <td className="px-5 py-2.5">
                  <p className="font-semibold text-slate-800 dark:text-slate-200">{o.id}</p>
                  <p className="text-xs text-slate-400">{o.product}</p>
                </td>
                <td className="px-3 py-2.5">
                  <p className="font-medium text-slate-700 dark:text-slate-300">{o.customer}</p>
                  <p className="text-xs text-slate-400">{o.date}</p>
                </td>
                <td className="px-3 py-2.5 font-semibold text-slate-800 dark:text-slate-200">
                  {money(o.amount)}
                </td>
                <td className="px-3 py-2.5">
                  <StatusBadge status={o.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        onClick={onViewAll}
        className="mt-3 self-start text-xs font-semibold text-indigo-600 transition hover:text-indigo-500 dark:text-indigo-400"
      >
        View all orders →
      </button>
    </div>
  );
}
