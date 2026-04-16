import React from 'react';
import { api } from '../api';

interface Deployment {
  id: any; operator: any; device: any; taken_at: any; returned_at: any; incident_ref: any; condition_on_return: any;
}

export default function DeploymentPage() {
  const [items, setItems] = React.useState<Deployment[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ operator: '', device: '', returned_at: '', incident_ref: '', condition_on_return: '' });

  const load = () => api.list<Deployment>('deployments').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('deployments', form);
    setForm({ operator: '', device: '', returned_at: '', incident_ref: '', condition_on_return: '' });
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
          <input name="operator" placeholder="operator" type="text" value={form.operator || ""} onChange={e => setForm({...form, operator: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="device" placeholder="device" type="text" value={form.device || ""} onChange={e => setForm({...form, device: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="returned_at" placeholder="returned_at" type="datetime-local" value={form.returned_at || ""} onChange={e => setForm({...form, returned_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="incident_ref" placeholder="incident_ref" type="text" value={form.incident_ref || ""} onChange={e => setForm({...form, incident_ref: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="condition_on_return" placeholder="condition_on_return" type="text" value={form.condition_on_return || ""} onChange={e => setForm({...form, condition_on_return: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">operator</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">device</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">taken_at</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">returned_at</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">incident_ref</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">condition_on_return</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.operator ?? "")}</td> <td className="p-2 text-sm">{String(item.device ?? "")}</td> <td className="p-2 text-sm">{String(item.taken_at ?? "")}</td> <td className="p-2 text-sm">{String(item.returned_at ?? "")}</td> <td className="p-2 text-sm">{String(item.incident_ref ?? "")}</td> <td className="p-2 text-sm">{String(item.condition_on_return ?? "")}</td>
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
