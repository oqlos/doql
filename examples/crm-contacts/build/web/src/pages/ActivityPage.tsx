import React from 'react';
import { api } from '../api';

interface Activity {
  id: any; type: any; contact: any; deal: any; subject: any; description: any; due_date: any; completed: any; assigned_to: any; created: any;
}

export default function ActivityPage() {
  const [items, setItems] = React.useState<Activity[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ type: '', contact: '', deal: '', subject: '', description: '', due_date: '', completed: '', assigned_to: '' });

  const load = () => api.list<Activity>('activitys').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('activitys', form);
    setForm({ type: '', contact: '', deal: '', subject: '', description: '', due_date: '', completed: '', assigned_to: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('activitys', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Activitys</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="type" placeholder="type" type="text" value={form.type || ""} onChange={e => setForm({...form, type: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="contact" placeholder="contact" type="text" value={form.contact || ""} onChange={e => setForm({...form, contact: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="deal" placeholder="deal" type="text" value={form.deal || ""} onChange={e => setForm({...form, deal: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="subject" placeholder="subject" type="text" value={form.subject || ""} onChange={e => setForm({...form, subject: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="description" placeholder="description" type="text" value={form.description || ""} onChange={e => setForm({...form, description: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="due_date" placeholder="due_date" type="datetime-local" value={form.due_date || ""} onChange={e => setForm({...form, due_date: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="completed" checked={!!form.completed} onChange={e => setForm({...form, completed: e.target.checked})} /> completed</label>
  <input name="assigned_to" placeholder="assigned_to" type="text" value={form.assigned_to || ""} onChange={e => setForm({...form, assigned_to: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">type</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">contact</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">deal</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">subject</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">description</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">due_date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">completed</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.type ?? "")}</td> <td className="p-2 text-sm">{String(item.contact ?? "")}</td> <td className="p-2 text-sm">{String(item.deal ?? "")}</td> <td className="p-2 text-sm">{String(item.subject ?? "")}</td> <td className="p-2 text-sm">{String(item.description ?? "")}</td> <td className="p-2 text-sm">{String(item.due_date ?? "")}</td> <td className="p-2 text-sm">{String(item.completed ?? "")}</td>
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
