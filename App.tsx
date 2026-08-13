import { useState } from "react";
import { ThemeProvider } from "./context/ThemeContext";
import {
  initialCustomers,
  initialOrders,
  initialProducts,
  type Customer,
  type Order,
  type Product,
} from "./data/mockData";
import { PAGE_META, type Page } from "./types";
import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";
import DashboardPage from "./components/dashboard/DashboardPage";
import ProductsPage from "./components/products/ProductsPage";
import OrdersPage from "./components/orders/OrdersPage";
import CustomersPage from "./components/customers/CustomersPage";
import AnalyticsPage from "./components/analytics/AnalyticsPage";
import SettingsPage from "./components/settings/SettingsPage";

export default function App() {
  return (
    <ThemeProvider>
      <Shell />
    </ThemeProvider>
  );
}

function Shell() {
  const [page, setPage] = useState<Page>("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [products, setProducts] = useState<Product[]>(initialProducts);
  const [orders, setOrders] = useState<Order[]>(initialOrders);
  const [customers, setCustomers] = useState<Customer[]>(initialCustomers);

  const navigate = (p: Page) => {
    setPage(p);
    setSidebarOpen(false);
    window.scrollTo({ top: 0 });
  };

  const pendingCount = orders.filter((o) => o.status === "Pending").length;
  const lowStockCount = products.filter((p) => p.stock <= 10).length;
  const meta = PAGE_META[page];

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 transition-colors dark:bg-slate-950 dark:text-slate-100">
      <Sidebar
        page={page}
        onNavigate={navigate}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        pendingCount={pendingCount}
        lowStockCount={lowStockCount}
      />

      <div className="flex min-h-screen flex-col lg:pl-64">
        <Header
          title={meta.title}
          subtitle={meta.subtitle}
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="flex-1 px-4 py-6 sm:px-6">
          <div className="mx-auto w-full max-w-7xl">
            {page === "dashboard" && (
              <DashboardPage products={products} orders={orders} onNavigate={navigate} />
            )}
            {page === "products" && (
              <ProductsPage products={products} setProducts={setProducts} />
            )}
            {page === "orders" && <OrdersPage orders={orders} setOrders={setOrders} />}
            {page === "customers" && (
              <CustomersPage customers={customers} setCustomers={setCustomers} />
            )}
            {page === "analytics" && <AnalyticsPage products={products} />}
            {page === "settings" && <SettingsPage />}
          </div>
        </main>

        <footer className="border-t border-slate-200 px-6 py-4 text-center text-xs text-slate-400 dark:border-slate-800">
          © 2026 AdminPro · E-Commerce Admin & Analytics Dashboard · Crafted for the hackathon 🚀
        </footer>
      </div>
    </div>
  );
}
