import React from 'react';
import { api } from '../api';

interface CylinderFill {
  id: any; cylinder: any; filled_at: any; pressure_bar: any; operator: any; quality_check: any; air_quality_cert: any;
}

export default function CylinderFillPage() {
  const [items, setItems] = React.useState<CylinderFill[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ cylinder: '', pressure_bar: '', operator: '', quality_check: '', air_quality_cert: '' });

  const load = () => api.list<CylinderFill>('cylinder-fills').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('cylinder-fills', form);
    setForm({ cylinder: '', pressure_bar: '', operator: '', quality_check: '', air_quality_cert: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('cylinder-fills', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">CylinderFills</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="cylinder" placeholder="cylinder" type="text" value={form.cylinder || ""} onChange={e => setForm({...form, cylinder: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="pressure_bar" placeholder="pressure_bar" type="text" value={form.pressure_bar || ""} onChange={e => setForm({...form, pressure_bar: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="operator" placeholder="operator" type="text" value={form.operator || ""} onChange={e => setForm({...form, operator: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="quality_check" checked={!!form.quality_check} onChange={e => setForm({...form, quality_check: e.target.checked})} /> quality_check</label>
  <input name="air_quality_cert" placeholder="air_quality_cert" type="text" value={form.air_quality_cert || ""} onChange={e => setForm({...form, air_quality_cert: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">cylinder</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">filled_at</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">pressure_bar</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">operator</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">quality_check</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">air_quality_cert</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.cylinder ?? "")}</td> <td className="p-2 text-sm">{String(item.filled_at ?? "")}</td> <td className="p-2 text-sm">{String(item.pressure_bar ?? "")}</td> <td className="p-2 text-sm">{String(item.operator ?? "")}</td> <td className="p-2 text-sm">{String(item.quality_check ?? "")}</td> <td className="p-2 text-sm">{String(item.air_quality_cert ?? "")}</td>
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
