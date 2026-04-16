import React from 'react';
import { api } from '../api';

interface Exercise {
  id: any; operator: any; date: any; type: any; duration_minutes: any; equipment_used: any; pass: any; notes: any;
}

export default function ExercisePage() {
  const [items, setItems] = React.useState<Exercise[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ operator: '', date: '', type: '', duration_minutes: '', equipment_used: '', pass: '', notes: '' });

  const load = () => api.list<Exercise>('exercises').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('exercises', form);
    setForm({ operator: '', date: '', type: '', duration_minutes: '', equipment_used: '', pass: '', notes: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('exercises', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Exercises</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="operator" placeholder="operator" type="text" value={form.operator || ""} onChange={e => setForm({...form, operator: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="date" placeholder="date" type="date" value={form.date || ""} onChange={e => setForm({...form, date: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="type" placeholder="type" type="text" value={form.type || ""} onChange={e => setForm({...form, type: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="duration_minutes" placeholder="duration_minutes" type="number" value={form.duration_minutes || ""} onChange={e => setForm({...form, duration_minutes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="equipment_used" placeholder="equipment_used" type="text" value={form.equipment_used || ""} onChange={e => setForm({...form, equipment_used: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="pass" checked={!!form.pass} onChange={e => setForm({...form, pass: e.target.checked})} /> pass</label>
  <input name="notes" placeholder="notes" type="text" value={form.notes || ""} onChange={e => setForm({...form, notes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">operator</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">type</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">duration_minutes</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">equipment_used</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">pass</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">notes</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.operator ?? "")}</td> <td className="p-2 text-sm">{String(item.date ?? "")}</td> <td className="p-2 text-sm">{String(item.type ?? "")}</td> <td className="p-2 text-sm">{String(item.duration_minutes ?? "")}</td> <td className="p-2 text-sm">{String(item.equipment_used ?? "")}</td> <td className="p-2 text-sm">{String(item.pass ?? "")}</td> <td className="p-2 text-sm">{String(item.notes ?? "")}</td>
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
