import React from 'react';
import { api } from '../api';

interface Comment {
  id: any; post: any; author_name: any; author_email: any; content: any; approved: any; parent: any; created: any;
}

export default function CommentPage() {
  const [items, setItems] = React.useState<Comment[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ post: '', author_name: '', author_email: '', content: '', approved: '', parent: '' });

  const load = () => api.list<Comment>('comments').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('comments', form);
    setForm({ post: '', author_name: '', author_email: '', content: '', approved: '', parent: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('comments', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Comments</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="post" placeholder="post" type="text" value={form.post || ""} onChange={e => setForm({...form, post: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="author_name" placeholder="author_name" type="text" value={form.author_name || ""} onChange={e => setForm({...form, author_name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="author_email" placeholder="author_email" type="text" value={form.author_email || ""} onChange={e => setForm({...form, author_email: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="content" placeholder="content" type="text" value={form.content || ""} onChange={e => setForm({...form, content: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="approved" checked={!!form.approved} onChange={e => setForm({...form, approved: e.target.checked})} /> approved</label>
  <input name="parent" placeholder="parent" type="text" value={form.parent || ""} onChange={e => setForm({...form, parent: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">post</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">author_name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">author_email</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">content</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">approved</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">parent</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.post ?? "")}</td> <td className="p-2 text-sm">{String(item.author_name ?? "")}</td> <td className="p-2 text-sm">{String(item.author_email ?? "")}</td> <td className="p-2 text-sm">{String(item.content ?? "")}</td> <td className="p-2 text-sm">{String(item.approved ?? "")}</td> <td className="p-2 text-sm">{String(item.parent ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td>
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
