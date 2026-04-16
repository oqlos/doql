import React from 'react';
import { api } from '../api';

interface Telemetry {
  node: any; timestamp: any; cpu_load: any; memory_used: any; temperature_c: any; data: any;
}

export default function TelemetryPage() {
  const [items, setItems] = React.useState<Telemetry[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ node: '', cpu_load: '', memory_used: '', temperature_c: '', data: '' });

  const load = () => api.list<Telemetry>('telemetrys').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('telemetrys', form);
    setForm({ node: '', cpu_load: '', memory_used: '', temperature_c: '', data: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('telemetrys', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Telemetrys</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="node" placeholder="node" type="text" value={form.node || ""} onChange={e => setForm({...form, node: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="cpu_load" placeholder="cpu_load" type="number" value={form.cpu_load || ""} onChange={e => setForm({...form, cpu_load: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="memory_used" placeholder="memory_used" type="number" value={form.memory_used || ""} onChange={e => setForm({...form, memory_used: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="temperature_c" placeholder="temperature_c" type="number" value={form.temperature_c || ""} onChange={e => setForm({...form, temperature_c: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="data" placeholder="data" type="text" value={form.data || ""} onChange={e => setForm({...form, data: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">node</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">timestamp</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">cpu_load</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">memory_used</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">temperature_c</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">data</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.node ?? "")}</td> <td className="p-2 text-sm">{String(item.timestamp ?? "")}</td> <td className="p-2 text-sm">{String(item.cpu_load ?? "")}</td> <td className="p-2 text-sm">{String(item.memory_used ?? "")}</td> <td className="p-2 text-sm">{String(item.temperature_c ?? "")}</td> <td className="p-2 text-sm">{String(item.data ?? "")}</td>
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
