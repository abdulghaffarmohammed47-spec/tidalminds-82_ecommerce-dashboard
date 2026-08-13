export type Page = "dashboard" | "products" | "orders" | "customers" | "analytics" | "settings";

export const PAGE_META: Record<Page, { title: string; subtitle: string }> = {
  dashboard: { title: "Dashboard", subtitle: "Welcome back, Aisha! Here's your store at a glance." },
  products: { title: "Products & Inventory", subtitle: "Manage your catalog, stock levels and pricing." },
  orders: { title: "Order Management", subtitle: "Track, filter and update customer orders." },
  customers: { title: "Customers", subtitle: "Your customer directory and spending insights." },
  analytics: { title: "Analytics", subtitle: "Revenue trends, category mix and performance." },
  settings: { title: "Settings", subtitle: "Manage your profile, notifications and appearance." },
};
