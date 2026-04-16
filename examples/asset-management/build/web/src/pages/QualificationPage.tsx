import React from 'react';
import { api } from '../api';

interface Qualification {
  name: any; level: any; valid_until: any; certificate_file: any;
}

export default function QualificationPage() {
  const [items, setItems] = React.useState<Qualification[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', level: '', valid_until: '', certificate_file: '' });

  const load = () => api.list<Qualification>('qualifications').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('qualifications', form);
    setForm({ name: '', level: '', valid_until: '', certificate_file: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('qualifications', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Qualifications</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="level" placeholder="level" type="text" value={form.level || ""} onChange={e => setForm({...form, level: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="valid_until" placeholder="valid_until" type="date" value={form.valid_until || ""} onChange={e => setForm({...form, valid_until: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="certificate_file" placeholder="certificate_file" type="text" value={form.certificate_file || ""} onChange={e => setForm({...form, certificate_file: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">level</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">valid_until</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">certificate_file</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.level ?? "")}</td> <td className="p-2 text-sm">{String(item.valid_until ?? "")}</td> <td className="p-2 text-sm">{String(item.certificate_file ?? "")}</td>
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
