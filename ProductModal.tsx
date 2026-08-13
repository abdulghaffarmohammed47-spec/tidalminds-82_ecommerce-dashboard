import { useState } from "react";
import { X } from "lucide-react";
import { PRODUCT_CATEGORIES, type Product } from "../../data/mockData";

export default function ProductModal({
  product,
  onClose,
  onSave,
}: {
  product: Product | null; // null → add mode
  onClose: () => void;
  onSave: (p: Product) => void;
}) {
  const isAdd = product === null;
  const [form, setForm] = useState({
    name: product?.name ?? "",
    category: product?.category ?? PRODUCT_CATEGORIES[0],
    price: String(product?.price ?? ""),
    stock: String(product?.stock ?? ""),
    sku: product?.sku ?? "",
  });
  const [error, setError] = useState("");

  const set = (field: keyof typeof form, value: string) =>
    setForm((f) => ({ ...f, [field]: value }));

  const handleSave = () => {
    if (!form.name.trim()) {
      setError("Product name is required.");
      return;
    }
    const price = parseFloat(form.price);
    const stock = parseInt(form.stock, 10);
    if (Number.isNaN(price) || price < 0) {
      setError("Enter a valid price.");
      return;
    }
    if (Number.isNaN(stock) || stock < 0) {
      setError("Enter a valid stock quantity.");
      return;
    }
    onSave({
      id: product?.id ?? Date.now(),
      name: form.name.trim(),
      category: form.category,
      price,
      stock,
      sku: form.sku.trim() || `SKU-${Math.floor(1000 + Math.random() * 9000)}`,
      sold: product?.sold ?? 0,
      emoji: product?.emoji ?? "📦",
      tile: product?.tile ?? "from-slate-400 to-slate-600",
    });
  };

  const inputCls =
    "mt-1 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md animate-modal-in rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">
              {isAdd ? "Add Product" : "Edit Product"}
            </h2>
            <p className="text-xs text-slate-400">
              {isAdd ? "Create a new catalog item" : `Editing ${product?.sku}`}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <div className="space-y-4 px-6 py-5">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Product name
            </label>
            <input
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              placeholder="e.g. Wireless Headphones"
              className={inputCls}
              autoFocus
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Category
              </label>
              <select
                value={form.category}
                onChange={(e) => set("category", e.target.value)}
                className={inputCls}
              >
                {PRODUCT_CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                SKU
              </label>
              <input
                value={form.sku}
                onChange={(e) => set("sku", e.target.value)}
                placeholder="ELEC-019"
                className={inputCls}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Price ($)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={(e) => set("price", e.target.value)}
                placeholder="49.99"
                className={inputCls}
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                Stock
              </label>
              <input
                type="number"
                min="0"
                step="1"
                value={form.stock}
                onChange={(e) => set("stock", e.target.value)}
                placeholder="25"
                className={inputCls}
              />
            </div>
          </div>

          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-600 dark:bg-red-500/10 dark:text-red-400">
              {error}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
          <button
            onClick={onClose}
            className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-500"
          >
            {isAdd ? "Add Product" : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}
