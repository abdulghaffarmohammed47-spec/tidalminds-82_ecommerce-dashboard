import { useMemo, useState } from "react";
import { Search, UserRoundCheck, Users, Wallet } from "lucide-react";
import { money, type Customer } from "../../data/mockData";
import { CSVExportBtn, StatusBadge } from "../shared/ui";

const AVATAR_GRADIENTS = [
  "from-pink-500 to-rose-600",
  "from-indigo-500 to-violet-600",
  "from-emerald-500 to-teal-600",
  "from-amber-500 to-orange-600",
  "from-sky-500 to-blue-600",
  "from-fuchsia-500 to-purple-600",
];

export default function CustomersPage({
  customers,
  setCustomers,
}: {
  customers: Customer[];
  setCustomers: React.Dispatch<React.SetStateAction<Customer[]>>;
}) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(
    () =>
      customers.filter(
        (c) =>
          c.name.toLowerCase().includes(search.toLowerCase()) ||
          c.email.toLowerCase().includes(search.toLowerCase()) ||
          c.location.toLowerCase().includes(search.toLowerCase())
      ),
    [customers, search]
  );

  const activeCount = customers.filter((c) => c.status === "Active").length;
  const totalSpent = customers.reduce((s, c) => s + c.spent, 0);

  const toggleStatus = (id: number) =>
    setCustomers((prev) =>
      prev.map((c) =>
        c.id === id ? { ...c, status: c.status === "Active" ? "Inactive" : "Active" } : c
      )
    );

  const exportRows = filtered.map((c) => ({
    name: c.name,
    email: c.email,
    orders: c.orders,
    spent: c.spent,
    location: c.location,
    joined: c.joined,
    status: c.status,
  }));

  return (
    <div className="animate-fade-up space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: "Total customers", value: customers.length.toString(), icon: Users, tone: "from-indigo-500 to-violet-600" },
          { label: "Active customers", value: activeCount.toString(), icon: UserRoundCheck, tone: "from-emerald-500 to-teal-600" },
          { label: "Lifetime value (top 10)", value: money(totalSpent), icon: Wallet, tone: "from-amber-500 to-orange-600" },
        ].map((s) => (
          <div
            key={s.label}
            className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br text-white ${s.tone}`}>
              <s.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{s.label}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Card */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 p-4 dark:border-slate-800">
          <div className="relative min-w-52 flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search customers by name, email or location…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:bg-slate-800"
            />
          </div>
          <CSVExportBtn data={exportRows} filename="customers.csv" label="Export" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-left text-xs font-semibold uppercase tracking-wide text-slate-400 dark:border-slate-800 dark:bg-slate-800/40 dark:text-slate-500">
                <th className="px-5 py-3">Customer</th>
                <th className="px-3 py-3">Location</th>
                <th className="px-3 py-3">Orders</th>
                <th className="px-3 py-3">Total spent</th>
                <th className="px-3 py-3">Joined</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr
                  key={c.id}
                  className="border-b border-slate-50 transition hover:bg-slate-50/70 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br text-xs font-bold text-white ${
                          AVATAR_GRADIENTS[c.id % AVATAR_GRADIENTS.length]
                        }`}
                      >
                        {c.name.split(" ").map((n) => n[0]).join("")}
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-slate-800 dark:text-slate-200">
                          {c.name}
                        </p>
                        <p className="truncate text-xs text-slate-400">{c.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-slate-600 dark:text-slate-300">{c.location}</td>
                  <td className="px-3 py-3 text-slate-600 dark:text-slate-300">{c.orders}</td>
                  <td className="px-3 py-3 font-semibold text-slate-800 dark:text-slate-200">
                    {money(c.spent)}
                  </td>
                  <td className="px-3 py-3 text-slate-500 dark:text-slate-400">{c.joined}</td>
                  <td className="px-5 py-3">
                    <button onClick={() => toggleStatus(c.id)} aria-label={`Toggle status for ${c.name}`}>
                      <StatusBadge status={c.status} />
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-sm text-slate-400">
                    No customers found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-400 dark:border-slate-800">
          Showing {filtered.length} of {customers.length} customers · click a status badge to toggle it
        </div>
      </div>
    </div>
  );
}
