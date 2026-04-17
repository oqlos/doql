import React from 'react';
import { api } from '../api';

interface Product {
  id: any; name: any; slug: any; description: any; price: any; currency: any; stock: any; category: any; images: any; active: any; created: any; updated: any;
}

export default function ProductPage() {
  const [items, setItems] = React.useState<Product[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', slug: '', description: '', price: '', currency: '', stock: '', category: '', images: '', active: '' });

  const load = () => api.list<Product>('products').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('products', form);
    setForm({ name: '', slug: '', description: '', price: '', currency: '', stock: '', category: '', images: '', active: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('products', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Products</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="slug" placeholder="slug" type="text" value={form.slug || ""} onChange={e => setForm({...form, slug: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="description" placeholder="description" type="text" value={form.description || ""} onChange={e => setForm({...form, description: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="price" placeholder="price" type="text" value={form.price || ""} onChange={e => setForm({...form, price: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="currency" placeholder="currency" type="text" value={form.currency || ""} onChange={e => setForm({...form, currency: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="stock" placeholder="stock" type="number" value={form.stock || ""} onChange={e => setForm({...form, stock: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="category" placeholder="category" type="text" value={form.category || ""} onChange={e => setForm({...form, category: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="images" placeholder="images" type="text" value={form.images || ""} onChange={e => setForm({...form, images: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="active" checked={!!form.active} onChange={e => setForm({...form, active: e.target.checked})} /> active</label>
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">slug</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">description</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">price</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">currency</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">stock</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">category</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.slug ?? "")}</td> <td className="p-2 text-sm">{String(item.description ?? "")}</td> <td className="p-2 text-sm">{String(item.price ?? "")}</td> <td className="p-2 text-sm">{String(item.currency ?? "")}</td> <td className="p-2 text-sm">{String(item.stock ?? "")}</td> <td className="p-2 text-sm">{String(item.category ?? "")}</td>
                <td className="p-2">
                  <button onClick={() => handleDelete(item.id)} className="text-red-500 text-xs hover:underline">Delete</button>
                </td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={99} className="p-8 text-center text-gray-400">No items yet</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
