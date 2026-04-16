import React from 'react';
import { api } from '../api';

interface OTAUpdate {
  id: any; firmware: any; targets: any; status: any; started_at: any;
}

export default function OTAUpdatePage() {
  const [items, setItems] = React.useState<OTAUpdate[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ firmware: '', targets: '', status: '', started_at: '' });

  const load = () => api.list<OTAUpdate>('ota-updates').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('ota-updates', form);
    setForm({ firmware: '', targets: '', status: '', started_at: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('ota-updates', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">OTAUpdates</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="firmware" placeholder="firmware" type="text" value={form.firmware || ""} onChange={e => setForm({...form, firmware: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="targets" placeholder="targets" type="text" value={form.targets || ""} onChange={e => setForm({...form, targets: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="status" placeholder="status" type="text" value={form.status || ""} onChange={e => setForm({...form, status: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="started_at" placeholder="started_at" type="datetime-local" value={form.started_at || ""} onChange={e => setForm({...form, started_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">firmware</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">targets</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">status</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">started_at</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.firmware ?? "")}</td> <td className="p-2 text-sm">{String(item.targets ?? "")}</td> <td className="p-2 text-sm">{String(item.status ?? "")}</td> <td className="p-2 text-sm">{String(item.started_at ?? "")}</td>
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
