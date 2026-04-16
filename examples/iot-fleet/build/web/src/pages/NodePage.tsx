import React from 'react';
import { api } from '../api';

interface Node {
  id: any; hostname: any; location: any; tags: any; hardware_type: any; firmware_version: any; last_seen: any; peripherals: any;
}

export default function NodePage() {
  const [items, setItems] = React.useState<Node[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ hostname: '', location: '', tags: '', hardware_type: '', firmware_version: '', last_seen: '', peripherals: '' });

  const load = () => api.list<Node>('nodes').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('nodes', form);
    setForm({ hostname: '', location: '', tags: '', hardware_type: '', firmware_version: '', last_seen: '', peripherals: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('nodes', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Nodes</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="hostname" placeholder="hostname" type="text" value={form.hostname || ""} onChange={e => setForm({...form, hostname: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="location" placeholder="location" type="text" value={form.location || ""} onChange={e => setForm({...form, location: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="tags" placeholder="tags" type="text" value={form.tags || ""} onChange={e => setForm({...form, tags: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="hardware_type" placeholder="hardware_type" type="text" value={form.hardware_type || ""} onChange={e => setForm({...form, hardware_type: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="firmware_version" placeholder="firmware_version" type="text" value={form.firmware_version || ""} onChange={e => setForm({...form, firmware_version: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="last_seen" placeholder="last_seen" type="datetime-local" value={form.last_seen || ""} onChange={e => setForm({...form, last_seen: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="peripherals" placeholder="peripherals" type="text" value={form.peripherals || ""} onChange={e => setForm({...form, peripherals: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">hostname</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">location</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">tags</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">hardware_type</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">firmware_version</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">last_seen</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">peripherals</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.hostname ?? "")}</td> <td className="p-2 text-sm">{String(item.location ?? "")}</td> <td className="p-2 text-sm">{String(item.tags ?? "")}</td> <td className="p-2 text-sm">{String(item.hardware_type ?? "")}</td> <td className="p-2 text-sm">{String(item.firmware_version ?? "")}</td> <td className="p-2 text-sm">{String(item.last_seen ?? "")}</td> <td className="p-2 text-sm">{String(item.peripherals ?? "")}</td>
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
