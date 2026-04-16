import React from 'react';
import { api } from '../api';

interface Operator {
  id: any; name: any; personal_id: any; station: any; qualifications: any; hire_date: any; active: any;
}

export default function OperatorPage() {
  const [items, setItems] = React.useState<Operator[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', personal_id: '', station: '', qualifications: '', hire_date: '', active: '' });

  const load = () => api.list<Operator>('operators').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('operators', form);
    setForm({ name: '', personal_id: '', station: '', qualifications: '', hire_date: '', active: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('operators', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Operators</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="personal_id" placeholder="personal_id" type="text" value={form.personal_id || ""} onChange={e => setForm({...form, personal_id: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="station" placeholder="station" type="text" value={form.station || ""} onChange={e => setForm({...form, station: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="qualifications" placeholder="qualifications" type="text" value={form.qualifications || ""} onChange={e => setForm({...form, qualifications: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="hire_date" placeholder="hire_date" type="date" value={form.hire_date || ""} onChange={e => setForm({...form, hire_date: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="active" checked={!!form.active} onChange={e => setForm({...form, active: e.target.checked})} /> active</label>
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">personal_id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">station</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">qualifications</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">hire_date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">active</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.personal_id ?? "")}</td> <td className="p-2 text-sm">{String(item.station ?? "")}</td> <td className="p-2 text-sm">{String(item.qualifications ?? "")}</td> <td className="p-2 text-sm">{String(item.hire_date ?? "")}</td> <td className="p-2 text-sm">{String(item.active ?? "")}</td>
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
