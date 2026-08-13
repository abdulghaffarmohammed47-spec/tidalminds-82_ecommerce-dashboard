import { useState } from "react";
import { Bell, Check, Moon, Palette, ShieldAlert, Sun, UserRound } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import { cn } from "../../utils/cn";
import { ToggleSwitch } from "../shared/ui";

const inputCls =
  "mt-1 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100";

export default function SettingsPage() {
  const { dark, setDark } = useTheme();
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState({
    name: "Aisha Khan",
    email: "aisha@adminpro.com",
    role: "Super Admin",
    store: "AdminPro Store",
  });
  const [notifs, setNotifs] = useState({
    orders: true,
    inventory: true,
    marketing: false,
    weeklyReport: true,
  });

  const flashSaved = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const notifRows: { key: keyof typeof notifs; title: string; desc: string }[] = [
    { key: "orders", title: "New order alerts", desc: "Notify me when a customer places an order" },
    { key: "inventory", title: "Inventory alerts", desc: "Low stock and out-of-stock notifications" },
    { key: "marketing", title: "Marketing emails", desc: "Product tips, promotions and newsletters" },
    { key: "weeklyReport", title: "Weekly report", desc: "Send a summary of store performance every Monday" },
  ];

  return (
    <div className="animate-fade-up mx-auto max-w-3xl space-y-5">
      {/* Profile */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-4 dark:border-slate-800">
          <UserRound className="h-4 w-4 text-indigo-500" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-white">Profile</h3>
        </div>
        <div className="space-y-4 px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-pink-500 to-rose-600 text-lg font-bold text-white">
              AK
            </div>
            <div>
              <p className="text-sm font-bold text-slate-800 dark:text-white">{profile.name}</p>
              <p className="text-xs text-slate-400">{profile.role} · {profile.store}</p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Full name</label>
              <input value={profile.name} onChange={(e) => setProfile({ ...profile, name: e.target.value })} className={inputCls} />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Email</label>
              <input type="email" value={profile.email} onChange={(e) => setProfile({ ...profile, email: e.target.value })} className={inputCls} />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Role</label>
              <select value={profile.role} onChange={(e) => setProfile({ ...profile, role: e.target.value })} className={inputCls}>
                <option>Super Admin</option>
                <option>Admin</option>
                <option>Analyst</option>
                <option>Viewer</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">Store name</label>
              <input value={profile.store} onChange={(e) => setProfile({ ...profile, store: e.target.value })} className={inputCls} />
            </div>
          </div>
        </div>
      </section>

      {/* Appearance */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-4 dark:border-slate-800">
          <Palette className="h-4 w-4 text-indigo-500" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-white">Appearance</h3>
        </div>
        <div className="grid grid-cols-2 gap-3 px-6 py-5">
          <button
            onClick={() => setDark(false)}
            className={cn(
              "flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition",
              !dark
                ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10"
                : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600"
            )}
          >
            <Sun className={cn("h-6 w-6", !dark ? "text-indigo-500" : "text-slate-400")} />
            <span className={cn("text-xs font-bold", !dark ? "text-indigo-600 dark:text-indigo-300" : "text-slate-500 dark:text-slate-400")}>
              Light mode
            </span>
            <div className="h-10 w-full rounded-lg border border-slate-200 bg-white dark:border-slate-700" />
          </button>
          <button
            onClick={() => setDark(true)}
            className={cn(
              "flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition",
              dark
                ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-500/10"
                : "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600"
            )}
          >
            <Moon className={cn("h-6 w-6", dark ? "text-indigo-500" : "text-slate-400")} />
            <span className={cn("text-xs font-bold", dark ? "text-indigo-600 dark:text-indigo-300" : "text-slate-500 dark:text-slate-400")}>
              Dark mode
            </span>
            <div className="h-10 w-full rounded-lg border border-slate-700 bg-slate-800" />
          </button>
        </div>
      </section>

      {/* Notifications */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-3 border-b border-slate-100 px-6 py-4 dark:border-slate-800">
          <Bell className="h-4 w-4 text-indigo-500" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-white">Notifications</h3>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {notifRows.map((n) => (
            <div key={n.key} className="flex items-center justify-between gap-4 px-6 py-4">
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{n.title}</p>
                <p className="text-xs text-slate-400">{n.desc}</p>
              </div>
              <ToggleSwitch
                checked={notifs[n.key]}
                onChange={(v) => setNotifs({ ...notifs, [n.key]: v })}
                label={n.title}
              />
            </div>
          ))}
        </div>
      </section>

      {/* Danger zone */}
      <section className="overflow-hidden rounded-2xl border border-red-200 bg-white shadow-sm dark:border-red-500/25 dark:bg-slate-900">
        <div className="flex items-center gap-3 border-b border-red-100 px-6 py-4 dark:border-red-500/15">
          <ShieldAlert className="h-4 w-4 text-red-500" />
          <h3 className="text-sm font-bold text-red-600 dark:text-red-400">Danger zone</h3>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-5">
          <div>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">Reset demo data</p>
            <p className="text-xs text-slate-400">
              Clears all edits and restores the original sample dataset.
            </p>
          </div>
          <button
            onClick={() => {
              window.location.reload();
            }}
            className="rounded-xl border border-red-300 px-4 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50 dark:border-red-500/40 dark:text-red-400 dark:hover:bg-red-500/10"
          >
            Reset data
          </button>
        </div>
      </section>

      {/* Save bar */}
      <div className="flex items-center justify-end gap-3">
        {saved && (
          <span className="flex items-center gap-1.5 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
            <Check className="h-4 w-4" /> Settings saved
          </span>
        )}
        <button
          onClick={flashSaved}
          className="rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-500"
        >
          Save changes
        </button>
      </div>
    </div>
  );
}
