import React from 'react';
import { api } from '../api';

interface Post {
  id: any; title: any; slug: any; content: any; excerpt: any; author: any; category: any; tags: any; featured_image: any; published_at: any; created: any; updated: any;
}

export default function PostPage() {
  const [items, setItems] = React.useState<Post[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ title: '', slug: '', content: '', excerpt: '', author: '', category: '', tags: '', featured_image: '', published_at: '' });

  const load = () => api.list<Post>('posts').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('posts', form);
    setForm({ title: '', slug: '', content: '', excerpt: '', author: '', category: '', tags: '', featured_image: '', published_at: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('posts', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Posts</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="title" placeholder="title" type="text" value={form.title || ""} onChange={e => setForm({...form, title: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="slug" placeholder="slug" type="text" value={form.slug || ""} onChange={e => setForm({...form, slug: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="content" placeholder="content" type="text" value={form.content || ""} onChange={e => setForm({...form, content: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="excerpt" placeholder="excerpt" type="text" value={form.excerpt || ""} onChange={e => setForm({...form, excerpt: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="author" placeholder="author" type="text" value={form.author || ""} onChange={e => setForm({...form, author: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="category" placeholder="category" type="text" value={form.category || ""} onChange={e => setForm({...form, category: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="tags" placeholder="tags" type="text" value={form.tags || ""} onChange={e => setForm({...form, tags: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="featured_image" placeholder="featured_image" type="text" value={form.featured_image || ""} onChange={e => setForm({...form, featured_image: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="published_at" placeholder="published_at" type="datetime-local" value={form.published_at || ""} onChange={e => setForm({...form, published_at: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">title</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">slug</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">content</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">excerpt</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">author</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">category</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">tags</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.title ?? "")}</td> <td className="p-2 text-sm">{String(item.slug ?? "")}</td> <td className="p-2 text-sm">{String(item.content ?? "")}</td> <td className="p-2 text-sm">{String(item.excerpt ?? "")}</td> <td className="p-2 text-sm">{String(item.author ?? "")}</td> <td className="p-2 text-sm">{String(item.category ?? "")}</td> <td className="p-2 text-sm">{String(item.tags ?? "")}</td>
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
