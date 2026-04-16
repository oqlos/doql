import React from 'react';
import { api } from '../api';

interface CalibrationOrder {
  customer: any; instruments: any; received_date: any; due_date: any; priority: any; status: any; total_price: any; invoice_number: any;
}

export default function CalibrationOrderPage() {
  const [items, setItems] = React.useState<CalibrationOrder[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ customer: '', instruments: '', received_date: '', due_date: '', priority: '', status: '', total_price: '', invoice_number: '' });

  const load = () => api.list<CalibrationOrder>('calibration-orders').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('calibration-orders', form);
    setForm({ customer: '', instruments: '', received_date: '', due_date: '', priority: '', status: '', total_price: '', invoice_number: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('calibration-orders', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">CalibrationOrders</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="customer" placeholder="customer" type="text" value={form.customer || ""} onChange={e => setForm({...form, customer: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="instruments" placeholder="instruments" type="text" value={form.instruments || ""} onChange={e => setForm({...form, instruments: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="received_date" placeholder="received_date" type="date" value={form.received_date || ""} onChange={e => setForm({...form, received_date: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="due_date" placeholder="due_date" type="date" value={form.due_date || ""} onChange={e => setForm({...form, due_date: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="priority" placeholder="priority" type="text" value={form.priority || ""} onChange={e => setForm({...form, priority: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="status" placeholder="status" type="text" value={form.status || ""} onChange={e => setForm({...form, status: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="total_price" placeholder="total_price" type="text" value={form.total_price || ""} onChange={e => setForm({...form, total_price: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="invoice_number" placeholder="invoice_number" type="text" value={form.invoice_number || ""} onChange={e => setForm({...form, invoice_number: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">customer</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">instruments</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">received_date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">due_date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">priority</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">status</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">total_price</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">invoice_number</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.customer ?? "")}</td> <td className="p-2 text-sm">{String(item.instruments ?? "")}</td> <td className="p-2 text-sm">{String(item.received_date ?? "")}</td> <td className="p-2 text-sm">{String(item.due_date ?? "")}</td> <td className="p-2 text-sm">{String(item.priority ?? "")}</td> <td className="p-2 text-sm">{String(item.status ?? "")}</td> <td className="p-2 text-sm">{String(item.total_price ?? "")}</td> <td className="p-2 text-sm">{String(item.invoice_number ?? "")}</td>
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
