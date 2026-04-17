import React from 'react';
import { api } from '../api';

interface MediaFile {
  id: any; filename: any; mime_type: any; size: any; url: any; alt_text: any; uploaded_by: any; created: any;
}

export default function MediaFilePage() {
  const [items, setItems] = React.useState<MediaFile[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ filename: '', mime_type: '', size: '', url: '', alt_text: '', uploaded_by: '' });

  const load = () => api.list<MediaFile>('media-files').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('media-files', form);
    setForm({ filename: '', mime_type: '', size: '', url: '', alt_text: '', uploaded_by: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('media-files', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">MediaFiles</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="filename" placeholder="filename" type="text" value={form.filename || ""} onChange={e => setForm({...form, filename: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="mime_type" placeholder="mime_type" type="text" value={form.mime_type || ""} onChange={e => setForm({...form, mime_type: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="size" placeholder="size" type="number" value={form.size || ""} onChange={e => setForm({...form, size: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="url" placeholder="url" type="text" value={form.url || ""} onChange={e => setForm({...form, url: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="alt_text" placeholder="alt_text" type="text" value={form.alt_text || ""} onChange={e => setForm({...form, alt_text: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="uploaded_by" placeholder="uploaded_by" type="text" value={form.uploaded_by || ""} onChange={e => setForm({...form, uploaded_by: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">filename</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">mime_type</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">size</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">url</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">alt_text</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">uploaded_by</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.filename ?? "")}</td> <td className="p-2 text-sm">{String(item.mime_type ?? "")}</td> <td className="p-2 text-sm">{String(item.size ?? "")}</td> <td className="p-2 text-sm">{String(item.url ?? "")}</td> <td className="p-2 text-sm">{String(item.alt_text ?? "")}</td> <td className="p-2 text-sm">{String(item.uploaded_by ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td>
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
