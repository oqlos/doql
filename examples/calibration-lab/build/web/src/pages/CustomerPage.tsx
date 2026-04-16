import React from 'react';
import { api } from '../api';

interface Customer {
  name: any; address: any; contact_email: any; vat_id: any; active: any;
}

export default function CustomerPage() {
  const [items, setItems] = React.useState<Customer[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', address: '', contact_email: '', vat_id: '', active: '' });

  const load = () => api.list<Customer>('customers').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('customers', form);
    setForm({ name: '', address: '', contact_email: '', vat_id: '', active: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('customers', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Customers</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="address" placeholder="address" type="text" value={form.address || ""} onChange={e => setForm({...form, address: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="contact_email" placeholder="contact_email" type="text" value={form.contact_email || ""} onChange={e => setForm({...form, contact_email: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="vat_id" placeholder="vat_id" type="text" value={form.vat_id || ""} onChange={e => setForm({...form, vat_id: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="active" checked={!!form.active} onChange={e => setForm({...form, active: e.target.checked})} /> active</label>
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">address</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">contact_email</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">vat_id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">active</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.address ?? "")}</td> <td className="p-2 text-sm">{String(item.contact_email ?? "")}</td> <td className="p-2 text-sm">{String(item.vat_id ?? "")}</td> <td className="p-2 text-sm">{String(item.active ?? "")}</td>
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
