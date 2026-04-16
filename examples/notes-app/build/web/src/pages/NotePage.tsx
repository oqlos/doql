import React from 'react';
import { api } from '../api';

interface Note {
  id: any; notebook: any; title: any; body: any; pinned: any; tags: any; created: any; updated: any;
}

export default function NotePage() {
  const [items, setItems] = React.useState<Note[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ notebook: '', title: '', body: '', pinned: '', tags: '' });

  const load = () => api.list<Note>('notes').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('notes', form);
    setForm({ notebook: '', title: '', body: '', pinned: '', tags: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('notes', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Notes</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="notebook" placeholder="notebook" type="text" value={form.notebook || ""} onChange={e => setForm({...form, notebook: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="title" placeholder="title" type="text" value={form.title || ""} onChange={e => setForm({...form, title: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="body" placeholder="body" type="text" value={form.body || ""} onChange={e => setForm({...form, body: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="pinned" checked={!!form.pinned} onChange={e => setForm({...form, pinned: e.target.checked})} /> pinned</label>
  <input name="tags" placeholder="tags" type="text" value={form.tags || ""} onChange={e => setForm({...form, tags: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">notebook</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">title</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">body</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">pinned</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">tags</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">updated</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.notebook ?? "")}</td> <td className="p-2 text-sm">{String(item.title ?? "")}</td> <td className="p-2 text-sm">{String(item.body ?? "")}</td> <td className="p-2 text-sm">{String(item.pinned ?? "")}</td> <td className="p-2 text-sm">{String(item.tags ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td> <td className="p-2 text-sm">{String(item.updated ?? "")}</td>
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
