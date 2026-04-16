import React from 'react';
import { api } from '../api';

interface FirmwareBuild {
  id: any; version: any; release_notes: any; image_url: any; signature: any; targets: any; tested: any;
}

export default function FirmwareBuildPage() {
  const [items, setItems] = React.useState<FirmwareBuild[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ version: '', release_notes: '', image_url: '', signature: '', targets: '', tested: '' });

  const load = () => api.list<FirmwareBuild>('firmware-builds').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('firmware-builds', form);
    setForm({ version: '', release_notes: '', image_url: '', signature: '', targets: '', tested: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('firmware-builds', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">FirmwareBuilds</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="version" placeholder="version" type="text" value={form.version || ""} onChange={e => setForm({...form, version: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="release_notes" placeholder="release_notes" type="text" value={form.release_notes || ""} onChange={e => setForm({...form, release_notes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="image_url" placeholder="image_url" type="text" value={form.image_url || ""} onChange={e => setForm({...form, image_url: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="signature" placeholder="signature" type="text" value={form.signature || ""} onChange={e => setForm({...form, signature: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="targets" placeholder="targets" type="text" value={form.targets || ""} onChange={e => setForm({...form, targets: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <label className="flex items-center gap-2"><input type="checkbox" name="tested" checked={!!form.tested} onChange={e => setForm({...form, tested: e.target.checked})} /> tested</label>
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">version</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">release_notes</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">image_url</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">signature</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">targets</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">tested</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.version ?? "")}</td> <td className="p-2 text-sm">{String(item.release_notes ?? "")}</td> <td className="p-2 text-sm">{String(item.image_url ?? "")}</td> <td className="p-2 text-sm">{String(item.signature ?? "")}</td> <td className="p-2 text-sm">{String(item.targets ?? "")}</td> <td className="p-2 text-sm">{String(item.tested ?? "")}</td>
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
