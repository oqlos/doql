import React from 'react';
import { api } from '../api';

interface ReferenceStandard {
  id: any; instrument: any; traceability_chain: any; uncertainty_budget: any; certificate_pdf: any; valid_until: any;
}

export default function ReferenceStandardPage() {
  const [items, setItems] = React.useState<ReferenceStandard[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ instrument: '', traceability_chain: '', uncertainty_budget: '', certificate_pdf: '', valid_until: '' });

  const load = () => api.list<ReferenceStandard>('reference-standards').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('reference-standards', form);
    setForm({ instrument: '', traceability_chain: '', uncertainty_budget: '', certificate_pdf: '', valid_until: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('reference-standards', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">ReferenceStandards</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="instrument" placeholder="instrument" type="text" value={form.instrument || ""} onChange={e => setForm({...form, instrument: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="traceability_chain" placeholder="traceability_chain" type="text" value={form.traceability_chain || ""} onChange={e => setForm({...form, traceability_chain: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="uncertainty_budget" placeholder="uncertainty_budget" type="text" value={form.uncertainty_budget || ""} onChange={e => setForm({...form, uncertainty_budget: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="certificate_pdf" placeholder="certificate_pdf" type="text" value={form.certificate_pdf || ""} onChange={e => setForm({...form, certificate_pdf: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="valid_until" placeholder="valid_until" type="date" value={form.valid_until || ""} onChange={e => setForm({...form, valid_until: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">instrument</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">traceability_chain</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">uncertainty_budget</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">certificate_pdf</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">valid_until</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.instrument ?? "")}</td> <td className="p-2 text-sm">{String(item.traceability_chain ?? "")}</td> <td className="p-2 text-sm">{String(item.uncertainty_budget ?? "")}</td> <td className="p-2 text-sm">{String(item.certificate_pdf ?? "")}</td> <td className="p-2 text-sm">{String(item.valid_until ?? "")}</td>
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
