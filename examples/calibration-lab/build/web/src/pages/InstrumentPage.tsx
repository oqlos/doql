import React from 'react';
import { api } from '../api';

interface Instrument {
  id: any; serial: any; manufacturer: any; model: any; category: any; range_min: any; range_max: any; unit: any; uncertainty_class: any; owner_organization: any; last_calibration: any; certificate_valid_until: any;
}

export default function InstrumentPage() {
  const [items, setItems] = React.useState<Instrument[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ serial: '', manufacturer: '', model: '', category: '', range_min: '', range_max: '', unit: '', uncertainty_class: '', owner_organization: '', last_calibration: '', certificate_valid_until: '' });

  const load = () => api.list<Instrument>('instruments').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('instruments', form);
    setForm({ serial: '', manufacturer: '', model: '', category: '', range_min: '', range_max: '', unit: '', uncertainty_class: '', owner_organization: '', last_calibration: '', certificate_valid_until: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('instruments', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Instruments</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="serial" placeholder="serial" type="text" value={form.serial || ""} onChange={e => setForm({...form, serial: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="manufacturer" placeholder="manufacturer" type="text" value={form.manufacturer || ""} onChange={e => setForm({...form, manufacturer: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="model" placeholder="model" type="text" value={form.model || ""} onChange={e => setForm({...form, model: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="category" placeholder="category" type="text" value={form.category || ""} onChange={e => setForm({...form, category: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="range_min" placeholder="range_min" type="text" value={form.range_min || ""} onChange={e => setForm({...form, range_min: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="range_max" placeholder="range_max" type="text" value={form.range_max || ""} onChange={e => setForm({...form, range_max: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="unit" placeholder="unit" type="text" value={form.unit || ""} onChange={e => setForm({...form, unit: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="uncertainty_class" placeholder="uncertainty_class" type="text" value={form.uncertainty_class || ""} onChange={e => setForm({...form, uncertainty_class: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="owner_organization" placeholder="owner_organization" type="text" value={form.owner_organization || ""} onChange={e => setForm({...form, owner_organization: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="last_calibration" placeholder="last_calibration" type="date" value={form.last_calibration || ""} onChange={e => setForm({...form, last_calibration: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="certificate_valid_until" placeholder="certificate_valid_until" type="date" value={form.certificate_valid_until || ""} onChange={e => setForm({...form, certificate_valid_until: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">serial</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">manufacturer</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">model</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">category</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">range_min</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">range_max</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">unit</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">uncertainty_class</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.serial ?? "")}</td> <td className="p-2 text-sm">{String(item.manufacturer ?? "")}</td> <td className="p-2 text-sm">{String(item.model ?? "")}</td> <td className="p-2 text-sm">{String(item.category ?? "")}</td> <td className="p-2 text-sm">{String(item.range_min ?? "")}</td> <td className="p-2 text-sm">{String(item.range_max ?? "")}</td> <td className="p-2 text-sm">{String(item.unit ?? "")}</td> <td className="p-2 text-sm">{String(item.uncertainty_class ?? "")}</td>
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
