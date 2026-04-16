import React from 'react';
import { api } from '../api';

interface Deployment {
  id: any; name: any; scenario: any; target_filter: any; schedule: any; last_run: any;
}

export default function DeploymentPage() {
  const [items, setItems] = React.useState<Deployment[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', scenario: '', target_filter: '', schedule: '', last_run: '' });

  const load = () => api.list<Deployment>('deployments').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('deployments', form);
    setForm({ name: '', scenario: '', target_filter: '', schedule: '', last_run: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('deployments', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Deployments</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="scenario" placeholder="scenario" type="text" value={form.scenario || ""} onChange={e => setForm({...form, scenario: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="target_filter" placeholder="target_filter" type="text" value={form.target_filter || ""} onChange={e => setForm({...form, target_filter: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="schedule" placeholder="schedule" type="text" value={form.schedule || ""} onChange={e => setForm({...form, schedule: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="last_run" placeholder="last_run" type="datetime-local" value={form.last_run || ""} onChange={e => setForm({...form, last_run: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">scenario</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">target_filter</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">schedule</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">last_run</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.scenario ?? "")}</td> <td className="p-2 text-sm">{String(item.target_filter ?? "")}</td> <td className="p-2 text-sm">{String(item.schedule ?? "")}</td> <td className="p-2 text-sm">{String(item.last_run ?? "")}</td>
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
