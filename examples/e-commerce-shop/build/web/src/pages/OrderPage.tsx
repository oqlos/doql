import React from 'react';
import { api } from '../api';

interface Order {
  id: any; customer: any; status: any; items: any; total: any; currency: any; shipping_address: any; payment_method: any; paid_at: any; shipped_at: any; created: any;
}

export default function OrderPage() {
  const [items, setItems] = React.useState<Order[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ customer: '', status: '', items: '', total: '', currency: '', shipping_address: '', payment_method: '', paid_at: '', shipped_at: '' });

  const load = () => api.list<Order>('orders').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('orders', form);
    setForm({ customer: '', status: '', items: '', total: '', currency: '', shipping_address: '', payment_method: '', paid_at: '', shipped_at: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('orders', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Orders</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="customer" placeholder="customer" type="text" value={form.customer || ""} onChange={e => setForm({...form, customer: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="status" placeholder="status" type="text" value={form.status || ""} onChange={e => setForm({...form, status: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="items" placeholder="items" type="text" value={form.items || ""} onChange={e => setForm({...form, items: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="total" placeholder="total" type="text" value={form.total || ""} onChange={e => setForm({...form, total: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="currency" placeholder="currency" type="text" value={form.currency || ""} onChange={e => setForm({...form, currency: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="shipping_address" placeholder="shipping_address" type="text" value={form.shipping_address || ""} onChange={e => setForm({...form, shipping_address: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="payment_method" placeholder="payment_method" type="text" value={form.payment_method || ""} onChange={e => setForm({...form, payment_method: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="paid_at" placeholder="paid_at" type="datetime-local" value={form.paid_at || ""} onChange={e => setForm({...form, paid_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="shipped_at" placeholder="shipped_at" type="datetime-local" value={form.shipped_at || ""} onChange={e => setForm({...form, shipped_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">customer</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">status</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">items</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">total</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">currency</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">shipping_address</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">payment_method</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.customer ?? "")}</td> <td className="p-2 text-sm">{String(item.status ?? "")}</td> <td className="p-2 text-sm">{String(item.items ?? "")}</td> <td className="p-2 text-sm">{String(item.total ?? "")}</td> <td className="p-2 text-sm">{String(item.currency ?? "")}</td> <td className="p-2 text-sm">{String(item.shipping_address ?? "")}</td> <td className="p-2 text-sm">{String(item.payment_method ?? "")}</td>
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
