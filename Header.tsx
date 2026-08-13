import { useState } from "react";
import { Bell, ChevronDown, Menu, Moon, Search, Sun } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import { cn } from "../../utils/cn";

const NOTIFICATIONS = [
  { id: 1, emoji: "🚨", title: "2 products out of stock", time: "5 min ago", tone: "text-red-600 dark:text-red-400" },
  { id: 2, emoji: "🛒", title: "New order #ORD-1064 placed", time: "18 min ago", tone: "text-emerald-600 dark:text-emerald-400" },
  { id: 3, emoji: "📈", title: "Weekly revenue up 12.5%", time: "1 hr ago", tone: "text-indigo-600 dark:text-indigo-400" },
];

export default function Header({
  title,
  subtitle,
  onMenuClick,
}: {
  title: string;
  subtitle: string;
  onMenuClick: () => void;
}) {
  const { dark, toggle } = useTheme();
  const [notifOpen, setNotifOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80">
      <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
        <button
          onClick={onMenuClick}
          className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden dark:text-slate-400 dark:hover:bg-slate-800"
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="min-w-0">
          <h2 className="truncate text-lg font-bold text-slate-900 dark:text-white">{title}</h2>
          <p className="hidden truncate text-xs text-slate-500 sm:block dark:text-slate-400">
            {subtitle}
          </p>
        </div>

        <div className="ml-auto flex items-center gap-2 sm:gap-3">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search anything…"
              className="w-56 rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:focus:border-indigo-500 dark:focus:bg-slate-900"
            />
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggle}
            aria-label="Toggle dark mode"
            className="rounded-xl border border-slate-200 bg-white p-2 text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            {dark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setNotifOpen((o) => !o)}
              aria-label="Notifications"
              className="relative rounded-xl border border-slate-200 bg-white p-2 text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <Bell className="h-[18px] w-[18px]" />
              <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white">
                3
              </span>
            </button>
            {notifOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setNotifOpen(false)} />
                <div className="absolute right-0 z-50 mt-2 w-80 animate-modal-in overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
                  <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3 dark:border-slate-800">
                    <p className="text-sm font-bold text-slate-800 dark:text-white">Notifications</p>
                    <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-bold text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-400">
                      3 new
                    </span>
                  </div>
                  {NOTIFICATIONS.map((n) => (
                    <button
                      key={n.id}
                      onClick={() => setNotifOpen(false)}
                      className="flex w-full items-start gap-3 border-b border-slate-100 px-4 py-3 text-left transition hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/60"
                    >
                      <span className="text-lg">{n.emoji}</span>
                      <span className="min-w-0 flex-1">
                        <span className={cn("block truncate text-sm font-medium", n.tone)}>
                          {n.title}
                        </span>
                        <span className="block text-xs text-slate-400">{n.time}</span>
                      </span>
                    </button>
                  ))}
                  <button className="w-full py-2.5 text-center text-xs font-semibold text-indigo-600 transition hover:bg-indigo-50 dark:text-indigo-400 dark:hover:bg-indigo-500/10">
                    View all notifications
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Profile */}
          <button className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white py-1.5 pl-1.5 pr-2.5 transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-pink-500 to-rose-600 text-xs font-bold text-white">
              AK
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-xs font-semibold text-slate-800 dark:text-white">Aisha Khan</p>
              <p className="text-[10px] text-slate-400">Super Admin</p>
            </div>
            <ChevronDown className="hidden h-3.5 w-3.5 text-slate-400 sm:block" />
          </button>
        </div>
      </div>
    </header>
  );
}
