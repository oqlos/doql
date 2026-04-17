import React from 'react';
import { api } from '../api';

interface Contact {
  id: any; first_name: any; last_name: any; email: any; phone: any; company: any; position: any; tags: any; notes: any; source: any; created: any; updated: any;
}

export default function ContactPage() {
  const [items, setItems] = React.useState<Contact[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ first_name: '', last_name: '', email: '', phone: '', company: '', position: '', tags: '', notes: '', source: '' });

  const load = () => api.list<Contact>('contacts').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('contacts', form);
    setForm({ first_name: '', last_name: '', email: '', phone: '', company: '', position: '', tags: '', notes: '', source: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('contacts', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Contacts</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="first_name" placeholder="first_name" type="text" value={form.first_name || ""} onChange={e => setForm({...form, first_name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="last_name" placeholder="last_name" type="text" value={form.last_name || ""} onChange={e => setForm({...form, last_name: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="email" placeholder="email" type="text" value={form.email || ""} onChange={e => setForm({...form, email: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="phone" placeholder="phone" type="text" value={form.phone || ""} onChange={e => setForm({...form, phone: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="company" placeholder="company" type="text" value={form.company || ""} onChange={e => setForm({...form, company: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="position" placeholder="position" type="text" value={form.position || ""} onChange={e => setForm({...form, position: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="tags" placeholder="tags" type="text" value={form.tags || ""} onChange={e => setForm({...form, tags: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="notes" placeholder="notes" type="text" value={form.notes || ""} onChange={e => setForm({...form, notes: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="source" placeholder="source" type="text" value={form.source || ""} onChange={e => setForm({...form, source: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">first_name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">last_name</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">email</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">phone</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">company</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">position</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">tags</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.first_name ?? "")}</td> <td className="p-2 text-sm">{String(item.last_name ?? "")}</td> <td className="p-2 text-sm">{String(item.email ?? "")}</td> <td className="p-2 text-sm">{String(item.phone ?? "")}</td> <td className="p-2 text-sm">{String(item.company ?? "")}</td> <td className="p-2 text-sm">{String(item.position ?? "")}</td> <td className="p-2 text-sm">{String(item.tags ?? "")}</td>
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
