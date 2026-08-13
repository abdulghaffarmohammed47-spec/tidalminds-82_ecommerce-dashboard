// ─── Types ────────────────────────────────────────────────────────────────
export type OrderStatus = "Pending" | "Processing" | "Shipped" | "Delivered" | "Cancelled";

export interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  stock: number;
  sold: number;
  sku: string;
  emoji: string;
  tile: string; // tailwind gradient classes for the thumb
}

export interface Order {
  id: string;
  customer: string;
  email: string;
  product: string;
  amount: number;
  status: OrderStatus;
  date: string; // YYYY-MM-DD
  items: number;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  orders: number;
  spent: number;
  location: string;
  joined: string;
  status: "Active" | "Inactive";
}

export interface MonthlyPoint {
  month: string; // e.g. "Oct '25"
  date: string; // YYYY-MM-DD (first of month)
  revenue: number;
  orders: number;
  customers: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────
export const PRODUCT_CATEGORIES = ["Electronics", "Footwear", "Fitness", "Fashion", "Home & Kitchen"];

export const productStatus = (p: Product): "In Stock" | "Low Stock" | "Out of Stock" =>
  p.stock === 0 ? "Out of Stock" : p.stock <= 10 ? "Low Stock" : "In Stock";

export const money = (n: number) => `$${n.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;

// ─── Products ─────────────────────────────────────────────────────────────
export const initialProducts: Product[] = [
  { id: 1, name: "Wireless Headphones", category: "Electronics", price: 79.99, stock: 142, sold: 320, sku: "ELEC-001", emoji: "🎧", tile: "from-violet-500 to-indigo-500" },
  { id: 2, name: "Running Shoes", category: "Footwear", price: 59.99, stock: 8, sold: 215, sku: "FOOT-002", emoji: "👟", tile: "from-orange-400 to-rose-500" },
  { id: 3, name: "Yoga Mat", category: "Fitness", price: 29.99, stock: 0, sold: 180, sku: "FIT-003", emoji: "🧘", tile: "from-emerald-400 to-teal-500" },
  { id: 4, name: "Smart Watch", category: "Electronics", price: 199.99, stock: 64, sold: 264, sku: "ELEC-004", emoji: "⌚", tile: "from-sky-400 to-blue-600" },
  { id: 5, name: "Leather Backpack", category: "Fashion", price: 89.99, stock: 23, sold: 148, sku: "FASH-005", emoji: "🎒", tile: "from-amber-400 to-orange-600" },
  { id: 6, name: "Bluetooth Speaker", category: "Electronics", price: 49.99, stock: 5, sold: 192, sku: "ELEC-006", emoji: "🔊", tile: "from-cyan-400 to-sky-600" },
  { id: 7, name: "Denim Jacket", category: "Fashion", price: 74.99, stock: 31, sold: 121, sku: "FASH-007", emoji: "🧥", tile: "from-blue-400 to-indigo-600" },
  { id: 8, name: "Protein Powder", category: "Fitness", price: 39.99, stock: 3, sold: 98, sku: "FIT-008", emoji: "🥤", tile: "from-lime-400 to-green-600" },
  { id: 9, name: "Sunglasses", category: "Fashion", price: 24.99, stock: 96, sold: 156, sku: "FASH-009", emoji: "🕶️", tile: "from-slate-500 to-slate-700" },
  { id: 10, name: "Mechanical Keyboard", category: "Electronics", price: 129.99, stock: 17, sold: 187, sku: "ELEC-010", emoji: "⌨️", tile: "from-fuchsia-500 to-purple-600" },
  { id: 11, name: "Coffee Maker", category: "Home & Kitchen", price: 89.99, stock: 0, sold: 142, sku: "HOME-011", emoji: "☕", tile: "from-yellow-500 to-amber-600" },
  { id: 12, name: "Desk Lamp", category: "Home & Kitchen", price: 34.99, stock: 52, sold: 118, sku: "HOME-012", emoji: "💡", tile: "from-amber-300 to-yellow-500" },
  { id: 13, name: "Running Shorts", category: "Fitness", price: 19.99, stock: 7, sold: 76, sku: "FIT-013", emoji: "🩳", tile: "from-pink-400 to-rose-600" },
  { id: 14, name: "Gaming Mouse", category: "Electronics", price: 59.99, stock: 41, sold: 204, sku: "ELEC-014", emoji: "🖱️", tile: "from-red-400 to-rose-600" },
  { id: 15, name: "Water Bottle", category: "Fitness", price: 15.99, stock: 4, sold: 89, sku: "FIT-015", emoji: "🍶", tile: "from-teal-400 to-cyan-600" },
  { id: 16, name: "Scented Candle Set", category: "Home & Kitchen", price: 27.99, stock: 68, sold: 134, sku: "HOME-016", emoji: "🕯️", tile: "from-orange-300 to-amber-500" },
  { id: 17, name: "Trail Running Shoes", category: "Footwear", price: 84.99, stock: 12, sold: 97, sku: "FOOT-017", emoji: "🥾", tile: "from-green-500 to-emerald-600" },
  { id: 18, name: "Fitness Tracker", category: "Electronics", price: 99.99, stock: 9, sold: 173, sku: "ELEC-018", emoji: "📿", tile: "from-indigo-400 to-violet-600" },
];

// ─── Orders ───────────────────────────────────────────────────────────────
export const initialOrders: Order[] = [
  { id: "#ORD-1064", customer: "Sophia Turner", email: "sophia@email.com", product: "Wireless Headphones", amount: 79.99, status: "Delivered", date: "2026-09-24", items: 1 },
  { id: "#ORD-1063", customer: "Liam Carter", email: "liam@email.com", product: "Smart Watch", amount: 199.99, status: "Processing", date: "2026-09-24", items: 1 },
  { id: "#ORD-1062", customer: "Ava Martinez", email: "ava@email.com", product: "Running Shoes", amount: 59.99, status: "Shipped", date: "2026-09-23", items: 1 },
  { id: "#ORD-1061", customer: "Noah Wilson", email: "noah@email.com", product: "Mechanical Keyboard", amount: 129.99, status: "Delivered", date: "2026-09-23", items: 1 },
  { id: "#ORD-1060", customer: "Emma Brown", email: "emma@email.com", product: "Bluetooth Speaker", amount: 99.98, status: "Pending", date: "2026-09-22", items: 2 },
  { id: "#ORD-1059", customer: "Oliver Davis", email: "oliver@email.com", product: "Protein Powder", amount: 119.97, status: "Cancelled", date: "2026-09-21", items: 3 },
  { id: "#ORD-1058", customer: "Isabella Garcia", email: "isabella@email.com", product: "Leather Backpack", amount: 89.99, status: "Delivered", date: "2026-09-20", items: 1 },
  { id: "#ORD-1057", customer: "Ethan Moore", email: "ethan@email.com", product: "Gaming Mouse", amount: 59.99, status: "Delivered", date: "2026-09-19", items: 1 },
  { id: "#ORD-1056", customer: "Mia Jackson", email: "mia@email.com", product: "Yoga Mat", amount: 29.99, status: "Shipped", date: "2026-09-18", items: 1 },
  { id: "#ORD-1055", customer: "Lucas White", email: "lucas@email.com", product: "Fitness Tracker", amount: 99.99, status: "Processing", date: "2026-09-17", items: 1 },
  { id: "#ORD-1054", customer: "Amelia Harris", email: "amelia@email.com", product: "Denim Jacket", amount: 74.99, status: "Delivered", date: "2026-09-15", items: 1 },
  { id: "#ORD-1053", customer: "Mason Clark", email: "mason@email.com", product: "Smart Watch", amount: 199.99, status: "Delivered", date: "2026-09-14", items: 1 },
  { id: "#ORD-1052", customer: "Harper Lewis", email: "harper@email.com", product: "Scented Candle Set", amount: 55.98, status: "Pending", date: "2026-09-13", items: 2 },
  { id: "#ORD-1051", customer: "James Walker", email: "james@email.com", product: "Coffee Maker", amount: 89.99, status: "Cancelled", date: "2026-09-12", items: 1 },
  { id: "#ORD-1050", customer: "Evelyn Hall", email: "evelyn@email.com", product: "Sunglasses", amount: 49.98, status: "Delivered", date: "2026-09-10", items: 2 },
  { id: "#ORD-1049", customer: "Benjamin Young", email: "benjamin@email.com", product: "Wireless Headphones", amount: 79.99, status: "Shipped", date: "2026-09-09", items: 1 },
  { id: "#ORD-1048", customer: "Luna King", email: "luna@email.com", product: "Water Bottle", amount: 63.96, status: "Delivered", date: "2026-09-08", items: 4 },
  { id: "#ORD-1047", customer: "Henry Wright", email: "henry@email.com", product: "Running Shoes", amount: 119.98, status: "Delivered", date: "2026-09-06", items: 2 },
  { id: "#ORD-1046", customer: "Chloe Scott", email: "chloe@email.com", product: "Desk Lamp", amount: 34.99, status: "Pending", date: "2026-09-05", items: 1 },
  { id: "#ORD-1045", customer: "Alexander Green", email: "alex@email.com", product: "Mechanical Keyboard", amount: 129.99, status: "Delivered", date: "2026-09-03", items: 1 },
  { id: "#ORD-1044", customer: "Zoe Adams", email: "zoe@email.com", product: "Yoga Mat", amount: 29.99, status: "Delivered", date: "2026-08-30", items: 1 },
  { id: "#ORD-1043", customer: "William Baker", email: "william@email.com", product: "Bluetooth Speaker", amount: 49.99, status: "Shipped", date: "2026-08-28", items: 1 },
  { id: "#ORD-1042", customer: "Scarlett Nelson", email: "scarlett@email.com", product: "Leather Backpack", amount: 89.99, status: "Delivered", date: "2026-08-25", items: 1 },
  { id: "#ORD-1041", customer: "Jack Hill", email: "jack@email.com", product: "Trail Running Shoes", amount: 84.99, status: "Cancelled", date: "2026-08-22", items: 1 },
  { id: "#ORD-1040", customer: "Grace Campbell", email: "grace@email.com", product: "Sunglasses", amount: 24.99, status: "Delivered", date: "2026-08-18", items: 1 },
  { id: "#ORD-1039", customer: "Daniel Mitchell", email: "daniel@email.com", product: "Gaming Mouse", amount: 119.98, status: "Delivered", date: "2026-08-12", items: 2 },
  { id: "#ORD-1038", customer: "Sofia Roberts", email: "sofia@email.com", product: "Denim Jacket", amount: 74.99, status: "Delivered", date: "2026-08-08", items: 1 },
  { id: "#ORD-1037", customer: "Michael Turner", email: "michael@email.com", product: "Coffee Maker", amount: 89.99, status: "Shipped", date: "2026-08-02", items: 1 },
  { id: "#ORD-1036", customer: "Ellie Phillips", email: "ellie@email.com", product: "Fitness Tracker", amount: 99.99, status: "Delivered", date: "2026-07-28", items: 1 },
  { id: "#ORD-1035", customer: "Logan Evans", email: "logan@email.com", product: "Wireless Headphones", amount: 159.98, status: "Delivered", date: "2026-07-22", items: 2 },
];

// ─── Customers ────────────────────────────────────────────────────────────
export const initialCustomers: Customer[] = [
  { id: 1, name: "Sophia Turner", email: "sophia@email.com", orders: 24, spent: 2145.6, location: "New York, USA", joined: "2025-03-12", status: "Active" },
  { id: 2, name: "Liam Carter", email: "liam@email.com", orders: 19, spent: 1830.2, location: "London, UK", joined: "2025-06-04", status: "Active" },
  { id: 3, name: "Ava Martinez", email: "ava@email.com", orders: 31, spent: 3102.75, location: "Madrid, Spain", joined: "2024-11-21", status: "Active" },
  { id: 4, name: "Noah Wilson", email: "noah@email.com", orders: 12, spent: 964.4, location: "Toronto, Canada", joined: "2026-01-15", status: "Active" },
  { id: 5, name: "Emma Brown", email: "emma@email.com", orders: 8, spent: 512.9, location: "Sydney, Australia", joined: "2026-04-02", status: "Inactive" },
  { id: 6, name: "Oliver Davis", email: "oliver@email.com", orders: 15, spent: 1276.3, location: "Berlin, Germany", joined: "2025-09-18", status: "Active" },
  { id: 7, name: "Isabella Garcia", email: "isabella@email.com", orders: 27, spent: 2590.1, location: "Mexico City, Mexico", joined: "2024-08-30", status: "Active" },
  { id: 8, name: "Ethan Moore", email: "ethan@email.com", orders: 9, spent: 687.45, location: "Chicago, USA", joined: "2026-02-09", status: "Inactive" },
  { id: 9, name: "Mia Jackson", email: "mia@email.com", orders: 22, spent: 1958.8, location: "Paris, France", joined: "2025-05-27", status: "Active" },
  { id: 10, name: "Lucas White", email: "lucas@email.com", orders: 14, spent: 1102.15, location: "Tokyo, Japan", joined: "2025-12-01", status: "Active" },
];

// ─── Analytics ────────────────────────────────────────────────────────────
export const monthlyRevenue: MonthlyPoint[] = [
  { month: "Oct '25", date: "2025-10-01", revenue: 8200, orders: 82, customers: 64 },
  { month: "Nov '25", date: "2025-11-01", revenue: 9100, orders: 91, customers: 72 },
  { month: "Dec '25", date: "2025-12-01", revenue: 11400, orders: 114, customers: 89 },
  { month: "Jan '26", date: "2026-01-01", revenue: 7600, orders: 76, customers: 58 },
  { month: "Feb '26", date: "2026-02-01", revenue: 9800, orders: 98, customers: 76 },
  { month: "Mar '26", date: "2026-03-01", revenue: 10200, orders: 102, customers: 81 },
  { month: "Apr '26", date: "2026-04-01", revenue: 11500, orders: 115, customers: 92 },
  { month: "May '26", date: "2026-05-01", revenue: 10800, orders: 108, customers: 86 },
  { month: "Jun '26", date: "2026-06-01", revenue: 12400, orders: 124, customers: 99 },
  { month: "Jul '26", date: "2026-07-01", revenue: 13300, orders: 133, customers: 107 },
  { month: "Aug '26", date: "2026-08-01", revenue: 15200, orders: 152, customers: 124 },
  { month: "Sep '26", date: "2026-09-01", revenue: 16200, orders: 162, customers: 131 },
];

export const categoryRevenue = [
  { category: "Electronics", value: 42 },
  { category: "Footwear", value: 23 },
  { category: "Fitness", value: 18 },
  { category: "Fashion", value: 12 },
  { category: "Home & Kitchen", value: 5 },
];

export const dailyRevenue = [
  { day: "Mon", revenue: 3200 },
  { day: "Tue", revenue: 4100 },
  { day: "Wed", revenue: 3800 },
  { day: "Thu", revenue: 5200 },
  { day: "Fri", revenue: 6100 },
  { day: "Sat", revenue: 7400 },
  { day: "Sun", revenue: 5900 },
];
