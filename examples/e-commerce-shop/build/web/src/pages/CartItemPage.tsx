import React from 'react';
import { api } from '../api';

interface CartItem {
  id: any; session_id: any; product: any; quantity: any; created: any;
}

export default function CartItemPage() {
  const [items, setItems] = React.useState<CartItem[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ session_id: '', product: '', quantity: '' });

  const load = () => api.list<CartItem>('cart-items').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('cart-items', form);
    setForm({ session_id: '', product: '', quantity: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('cart-items', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">CartItems</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="session_id" placeholder="session_id" type="text" value={form.session_id || ""} onChange={e => setForm({...form, session_id: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="product" placeholder="product" type="text" value={form.product || ""} onChange={e => setForm({...form, product: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="quantity" placeholder="quantity" type="number" value={form.quantity || ""} onChange={e => setForm({...form, quantity: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">session_id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">product</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">quantity</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.session_id ?? "")}</td> <td className="p-2 text-sm">{String(item.product ?? "")}</td> <td className="p-2 text-sm">{String(item.quantity ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td>
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
