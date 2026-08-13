import { useMemo, useState } from "react";
import { AlertOctagon, AlertTriangle, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { PRODUCT_CATEGORIES, money, productStatus, type Product } from "../../data/mockData";
import { cn } from "../../utils/cn";
import { CSVExportBtn, StatusBadge } from "../shared/ui";
import ProductModal from "./ProductModal";

export default function ProductsPage({
  products,
  setProducts,
}: {
  products: Product[];
  setProducts: React.Dispatch<React.SetStateAction<Product[]>>;
}) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [modalProduct, setModalProduct] = useState<Product | null | undefined>(undefined);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  const outOfStock = products.filter((p) => p.stock === 0);
  const lowStock = products.filter((p) => p.stock > 0 && p.stock <= 10);

  const filtered = useMemo(
    () =>
      products.filter((p) => {
        const matchSearch =
          p.name.toLowerCase().includes(search.toLowerCase()) ||
          p.sku.toLowerCase().includes(search.toLowerCase());
        const matchCat = category === "All" || p.category === category;
        return matchSearch && matchCat;
      }),
    [products, search, category]
  );

  const handleSave = (updated: Product) => {
    setProducts((prev) => {
      const exists = prev.some((p) => p.id === updated.id);
      return exists ? prev.map((p) => (p.id === updated.id ? updated : p)) : [updated, ...prev];
    });
    setModalProduct(undefined);
  };

  const handleDelete = (id: number) => {
    if (confirmDelete === id) {
      setProducts((prev) => prev.filter((p) => p.id !== id));
      setConfirmDelete(null);
    } else {
      setConfirmDelete(id);
      setTimeout(() => setConfirmDelete((c) => (c === id ? null : c)), 2500);
    }
  };

  const exportRows = filtered.map((p) => ({
    sku: p.sku,
    name: p.name,
    category: p.category,
    price: p.price,
    stock: p.stock,
    sold: p.sold,
    status: productStatus(p),
  }));

  return (
    <div className="animate-fade-up space-y-5">
      {/* Alert banners */}
      {(outOfStock.length > 0 || lowStock.length > 0) && (
        <div className="grid gap-3 md:grid-cols-2">
          {outOfStock.length > 0 && (
            <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 dark:border-red-500/25 dark:bg-red-500/10">
              <AlertOctagon className="h-5 w-5 shrink-0 text-red-500" />
              <p className="text-sm font-semibold text-red-700 dark:text-red-400">
                <span className="font-bold">{outOfStock.length} product(s)</span> out of stock —{" "}
                {outOfStock.slice(0, 2).map((p) => p.name).join(", ")}
                {outOfStock.length > 2 && "…"}
              </p>
            </div>
          )}
          {lowStock.length > 0 && (
            <div className="flex items-center gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-500/25 dark:bg-amber-500/10">
              <AlertTriangle className="h-5 w-5 shrink-0 text-amber-500" />
              <p className="text-sm font-semibold text-amber-700 dark:text-amber-400">
                <span className="font-bold">{lowStock.length} product(s)</span> running low —
                {lowStock.slice(0, 2).map((p) => `${p.name} (${p.stock})`).join(", ")}
                {lowStock.length > 2 && "…"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Card */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 p-4 dark:border-slate-800">
          <div className="relative min-w-52 flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              placeholder="Search products by name or SKU…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:bg-slate-800"
            />
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 outline-none transition focus:border-indigo-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
          >
            <option value="All">All categories</option>
            {PRODUCT_CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
          <CSVExportBtn data={exportRows} filename="products.csv" label="Export" />
          <button
            onClick={() => setModalProduct(null)}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition hover:bg-indigo-500"
          >
            <Plus className="h-4 w-4" /> Add Product
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50/70 text-left text-xs font-semibold uppercase tracking-wide text-slate-400 dark:border-slate-800 dark:bg-slate-800/40 dark:text-slate-500">
                <th className="px-5 py-3">Product</th>
                <th className="px-3 py-3">Category</th>
                <th className="px-3 py-3">Price</th>
                <th className="px-3 py-3">Stock</th>
                <th className="px-3 py-3">Sold</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr
                  key={p.id}
                  className="border-b border-slate-50 transition hover:bg-slate-50/70 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-lg ${p.tile}`}
                      >
                        {p.emoji}
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-slate-800 dark:text-slate-200">
                          {p.name}
                        </p>
                        <p className="text-xs text-slate-400">{p.sku}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-slate-600 dark:text-slate-300">{p.category}</td>
                  <td className="px-3 py-3 font-semibold text-slate-800 dark:text-slate-200">
                    {money(p.price)}
                  </td>
                  <td className="px-3 py-3">
                    <span
                      className={cn(
                        "font-semibold",
                        p.stock <= 10
                          ? "font-bold text-red-500"
                          : "text-slate-700 dark:text-slate-300"
                      )}
                    >
                      {p.stock}
                    </span>
                  </td>
                  <td className="px-3 py-3 text-slate-500 dark:text-slate-400">{p.sold}</td>
                  <td className="px-3 py-3">
                    <StatusBadge status={productStatus(p)} />
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => setModalProduct(p)}
                        className="rounded-lg p-2 text-slate-400 transition hover:bg-indigo-50 hover:text-indigo-600 dark:hover:bg-indigo-500/10 dark:hover:text-indigo-400"
                        aria-label={`Edit ${p.name}`}
                      >
                        <Pencil className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(p.id)}
                        className={cn(
                          "rounded-lg p-2 transition",
                          confirmDelete === p.id
                            ? "bg-red-600 text-white hover:bg-red-500"
                            : "text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10 dark:hover:text-red-400"
                        )}
                        aria-label={`Delete ${p.name}`}
                      >
                        {confirmDelete === p.id ? (
                          <span className="px-1 text-xs font-bold">Sure?</span>
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-sm text-slate-400">
                    No products match your search. Try a different keyword or category.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Footer count */}
        <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-400 dark:border-slate-800">
          Showing {filtered.length} of {products.length} products
        </div>
      </div>

      {modalProduct !== undefined && (
        <ProductModal
          product={modalProduct}
          onClose={() => setModalProduct(undefined)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
