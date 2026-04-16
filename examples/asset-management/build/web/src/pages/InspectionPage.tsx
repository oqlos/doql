import React from 'react';
import { api } from '../api';

interface Inspection {
  id: any; device: any; operator: any; scenario_id: any; started_at: any; completed_at: any; result: any; measurements: any; notes: any; signed_by: any;
}

export default function InspectionPage() {
  const [items, setItems] = React.useState<Inspection[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ device: '', operator: '', scenario_id: '', completed_at: '', result: '', measurements: '', notes: '', signed_by: '' });

  const load = () => api.list<Inspection>('inspections').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('inspections', form);
    setForm({ device: '', operator: '', scenario_id: '', completed_at: '', result: '', measurements: '', notes: '', signed_by: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('inspections', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Inspections</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="device" placeholder="device" type="text" value={form.device || ""} onChange={e => setForm({...form, device: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="operator" placeholder="operator" type="text" value={form.operator || ""} onChange={e => setForm({...form, operator: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="scenario_id" placeholder="scenario_id" type="text" value={form.scenario_id || ""} onChange={e => setForm({...form, scenario_id: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="completed_at" placeholder="completed_at" type="datetime-local" value={form.completed_at || ""} onChange={e => setForm({...form, completed_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="result" placeholder="result" type="text" value={form.result || ""} onChange={e => setForm({...form, result: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="measurements" placeholder="measurements" type="text" value={form.measurements || ""} onChange={e => setForm({...form, measurements: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="notes" placeholder="notes" type="text" value={form.notes || ""} onChange={e => setForm({...form, notes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="signed_by" placeholder="signed_by" type="text" value={form.signed_by || ""} onChange={e => setForm({...form, signed_by: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">device</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">operator</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">scenario_id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">started_at</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">completed_at</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">result</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">measurements</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.device ?? "")}</td> <td className="p-2 text-sm">{String(item.operator ?? "")}</td> <td className="p-2 text-sm">{String(item.scenario_id ?? "")}</td> <td className="p-2 text-sm">{String(item.started_at ?? "")}</td> <td className="p-2 text-sm">{String(item.completed_at ?? "")}</td> <td className="p-2 text-sm">{String(item.result ?? "")}</td> <td className="p-2 text-sm">{String(item.measurements ?? "")}</td>
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
