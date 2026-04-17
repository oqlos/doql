import React from 'react';
import { api } from '../api';

interface Author {
  id: any; name: any; email: any; bio: any; avatar: any; created: any;
}

export default function AuthorPage() {
  const [items, setItems] = React.useState<Author[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', email: '', bio: '', avatar: '' });

  const load = () => api.list<Author>('authors').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('authors', form);
    setForm({ name: '', email: '', bio: '', avatar: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('authors', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Authors</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="email" placeholder="email" type="text" value={form.email || ""} onChange={e => setForm({...form, email: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="bio" placeholder="bio" type="text" value={form.bio || ""} onChange={e => setForm({...form, bio: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="avatar" placeholder="avatar" type="text" value={form.avatar || ""} onChange={e => setForm({...form, avatar: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">email</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">bio</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">avatar</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.email ?? "")}</td> <td className="p-2 text-sm">{String(item.bio ?? "")}</td> <td className="p-2 text-sm">{String(item.avatar ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td>
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
