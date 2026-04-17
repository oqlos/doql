import React from 'react';
import { api } from '../api';

interface Deal {
  id: any; title: any; contact: any; company: any; value: any; currency: any; stage: any; probability: any; expected_close: any; assigned_to: any; notes: any; created: any; updated: any;
}

export default function DealPage() {
  const [items, setItems] = React.useState<Deal[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ title: '', contact: '', company: '', value: '', currency: '', stage: '', probability: '', expected_close: '', assigned_to: '', notes: '' });

  const load = () => api.list<Deal>('deals').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('deals', form);
    setForm({ title: '', contact: '', company: '', value: '', currency: '', stage: '', probability: '', expected_close: '', assigned_to: '', notes: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('deals', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Deals</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="title" placeholder="title" type="text" value={form.title || ""} onChange={e => setForm({...form, title: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="contact" placeholder="contact" type="text" value={form.contact || ""} onChange={e => setForm({...form, contact: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="company" placeholder="company" type="text" value={form.company || ""} onChange={e => setForm({...form, company: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="value" placeholder="value" type="text" value={form.value || ""} onChange={e => setForm({...form, value: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="currency" placeholder="currency" type="text" value={form.currency || ""} onChange={e => setForm({...form, currency: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="stage" placeholder="stage" type="text" value={form.stage || ""} onChange={e => setForm({...form, stage: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="probability" placeholder="probability" type="number" value={form.probability || ""} onChange={e => setForm({...form, probability: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="expected_close" placeholder="expected_close" type="date" value={form.expected_close || ""} onChange={e => setForm({...form, expected_close: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="assigned_to" placeholder="assigned_to" type="text" value={form.assigned_to || ""} onChange={e => setForm({...form, assigned_to: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="notes" placeholder="notes" type="text" value={form.notes || ""} onChange={e => setForm({...form, notes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">title</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">contact</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">company</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">value</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">currency</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">stage</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">probability</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.title ?? "")}</td> <td className="p-2 text-sm">{String(item.contact ?? "")}</td> <td className="p-2 text-sm">{String(item.company ?? "")}</td> <td className="p-2 text-sm">{String(item.value ?? "")}</td> <td className="p-2 text-sm">{String(item.currency ?? "")}</td> <td className="p-2 text-sm">{String(item.stage ?? "")}</td> <td className="p-2 text-sm">{String(item.probability ?? "")}</td>
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
