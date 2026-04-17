import React from 'react';
import { api } from '../api';

interface Company {
  id: any; name: any; domain: any; industry: any; size: any; website: any; address: any; created: any;
}

export default function CompanyPage() {
  const [items, setItems] = React.useState<Company[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ name: '', domain: '', industry: '', size: '', website: '', address: '' });

  const load = () => api.list<Company>('companys').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('companys', form);
    setForm({ name: '', domain: '', industry: '', size: '', website: '', address: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('companys', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Companys</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="name" placeholder="name" type="text" value={form.name || ""} onChange={e => setForm({...form, name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="domain" placeholder="domain" type="text" value={form.domain || ""} onChange={e => setForm({...form, domain: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="industry" placeholder="industry" type="text" value={form.industry || ""} onChange={e => setForm({...form, industry: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="size" placeholder="size" type="text" value={form.size || ""} onChange={e => setForm({...form, size: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="website" placeholder="website" type="text" value={form.website || ""} onChange={e => setForm({...form, website: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="address" placeholder="address" type="text" value={form.address || ""} onChange={e => setForm({...form, address: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">domain</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">industry</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">size</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">website</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">address</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">created</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.name ?? "")}</td> <td className="p-2 text-sm">{String(item.domain ?? "")}</td> <td className="p-2 text-sm">{String(item.industry ?? "")}</td> <td className="p-2 text-sm">{String(item.size ?? "")}</td> <td className="p-2 text-sm">{String(item.website ?? "")}</td> <td className="p-2 text-sm">{String(item.address ?? "")}</td> <td className="p-2 text-sm">{String(item.created ?? "")}</td>
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
