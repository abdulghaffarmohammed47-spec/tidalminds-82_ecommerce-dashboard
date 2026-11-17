import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, X } from 'lucide-react';
import api from '../../lib/api';

interface AdminProduct {
  id: string;
  sku: string;
  title: string;
  brand: string;
  base_price: number;
  is_active: boolean;
  category: string;
  created_at: string;
}

export const ProductManagement: React.FC = () => {
  const [products, setProducts] = useState<AdminProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [categories, setCategories] = useState<{id: string, name: string}[]>([]);

  // Form State
  const [formData, setFormData] = useState({
    sku: '',
    title: '',
    slug: '',
    category_id: '',
    base_price: 0,
    is_active: true,
    description: ''
  });

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [prodRes, catRes] = await Promise.all([
        api.get('/api/admin/products'),
        api.get('/api/products/categories')
      ]);
      setProducts(prodRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error('Failed to fetch admin products', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/products', {
        ...formData,
        brand: 'Generic',
        variants: [{
          sku: `${formData.sku}-V1`,
          title: 'Default Variant',
          initial_stock: 10
        }]
      });
      setIsFormOpen(false);
      setFormData({ sku: '', title: '', slug: '', category_id: '', base_price: 0, is_active: true, description: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create product', err);
      alert('Failed to create product. Check console.');
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this product?')) {
      try {
        await api.delete(`/api/admin/products/${id}`);
        fetchData();
      } catch (err) {
        console.error('Failed to delete product', err);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center p-10">
        <div className="w-8 h-8 border-3 border-[#ebebeb] border-t-[#5433eb] rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-[-0.05em] text-[#000000]">Products</h2>
        <button
          onClick={() => setIsFormOpen(true)}
          className="flex items-center gap-2 bg-[#5433eb] text-[#ffffff] px-4 py-2 rounded-full font-semibold text-[14px] hover:bg-[#4524db] transition-colors"
        >
          <Plus size={18} />
          <span>Add Product</span>
        </button>
      </div>

      <div className="bg-[#ffffff] rounded-[28px] border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)] overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#f2f4f5] border-b border-[#ebebeb]">
              <th className="p-4 text-[13px] font-semibold text-[#787574]">SKU</th>
              <th className="p-4 text-[13px] font-semibold text-[#787574]">Title</th>
              <th className="p-4 text-[13px] font-semibold text-[#787574]">Category</th>
              <th className="p-4 text-[13px] font-semibold text-[#787574]">Price</th>
              <th className="p-4 text-[13px] font-semibold text-[#787574]">Status</th>
              <th className="p-4 text-[13px] font-semibold text-[#787574]">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#ebebeb]">
            {products.map(p => (
              <tr key={p.id} className="hover:bg-[#f2f4f5] transition-colors">
                <td className="p-4 text-[14px] font-medium text-[#000000]">{p.sku}</td>
                <td className="p-4 text-[14px] text-[#000000]">{p.title}</td>
                <td className="p-4 text-[14px] text-[#787574]">{p.category || '-'}</td>
                <td className="p-4 text-[14px] font-semibold text-[#000000]">${p.base_price.toFixed(2)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-[12px] font-semibold ${p.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {p.is_active ? 'Active' : 'Draft'}
                  </span>
                </td>
                <td className="p-4 flex gap-3">
                  <button className="text-[#5433eb] hover:text-[#4524db]" title="Edit"><Edit2 size={16}/></button>
                  <button onClick={() => handleDelete(p.id)} className="text-red-500 hover:text-red-700" title="Delete"><Trash2 size={16}/></button>
                </td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-[#787574]">No products found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isFormOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#ffffff] rounded-[28px] p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold tracking-[-0.05em] text-[#000000]">Add New Product</h3>
              <button onClick={() => setIsFormOpen(false)} className="text-[#787574] hover:text-[#000000]">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleCreateProduct} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[13px] font-medium text-[#787574] mb-1">SKU</label>
                  <input required type="text" value={formData.sku} onChange={e => setFormData({...formData, sku: e.target.value})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]" />
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-[#787574] mb-1">Title</label>
                  <input required type="text" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value, slug: e.target.value.toLowerCase().replace(/\s+/g, '-')})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]" />
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-[#787574] mb-1">Slug</label>
                  <input required type="text" value={formData.slug} onChange={e => setFormData({...formData, slug: e.target.value})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]" />
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-[#787574] mb-1">Category</label>
                  <select required value={formData.category_id} onChange={e => setFormData({...formData, category_id: e.target.value})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]">
                    <option value="">Select Category</option>
                    {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-[#787574] mb-1">Base Price ($)</label>
                  <input required type="number" step="0.01" value={formData.base_price} onChange={e => setFormData({...formData, base_price: parseFloat(e.target.value)})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]" />
                </div>
                <div className="flex items-center gap-2 mt-6">
                  <input type="checkbox" id="isActive" checked={formData.is_active} onChange={e => setFormData({...formData, is_active: e.target.checked})} className="w-4 h-4 rounded border-[#ebebeb] text-[#5433eb] focus:ring-[#5433eb]" />
                  <label htmlFor="isActive" className="text-[14px] font-medium text-[#000000]">Active Status</label>
                </div>
              </div>
              <div>
                <label className="block text-[13px] font-medium text-[#787574] mb-1">Description (MongoDB)</label>
                <textarea rows={3} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="w-full px-4 py-2 border border-[#ebebeb] rounded-[14px] bg-[#f2f4f5] text-[#000000] focus:outline-none focus:border-[#5433eb]"></textarea>
              </div>

              <div className="flex justify-end pt-4">
                <button type="submit" className="bg-[#5433eb] text-[#ffffff] px-8 py-3 rounded-[9999px] font-bold tracking-[-0.01em] hover:bg-[#4524db] transition-colors">
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
