import React from 'react';
import { api } from '../api';

interface User {
  id: any; name: any; email: any; role: any; active: any;
}

export default function UserPage() {
  const [items, setItems] = React.useState<User[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', email: '', role: '', active: '' });

  const load = () => api.list<User>('users').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('users', form);
    setForm({ name: '', email: '', role: '', active: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('users', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Users</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="email" placeholder="email" type="text" value={form.email || ""} onChange={e => setForm({...form, email: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="role" placeholder="role" type="text" value={form.role || ""} onChange={e => setForm({...form, role: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="active" checked={!!form.active} onChange={e => setForm({...form, active: e.target.checked})} /> active</label>
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">email</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">role</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">active</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.email ?? "")}</td> <td className="p-2 text-sm">{String(item.role ?? "")}</td> <td className="p-2 text-sm">{String(item.active ?? "")}</td>
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
