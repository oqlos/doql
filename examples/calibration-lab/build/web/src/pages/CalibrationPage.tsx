import React from 'react';
import { api } from '../api';

interface Calibration {
  id: any; instrument: any; performed_by: any; reviewed_by: any; reference_used: any; scenario: any; date: any; measurements: any; uncertainty_calculation: any; result: any; certificate_number: any;
}

export default function CalibrationPage() {
  const [items, setItems] = React.useState<Calibration[]>([]);
  const [showForm, setShowForm] = React.useState(false);
  const [form, setForm] = React.useState<any>({ instrument: '', performed_by: '', reviewed_by: '', reference_used: '', scenario: '', measurements: '', uncertainty_calculation: '', result: '' });

  const load = () => api.list<Calibration>('calibrations').then(setItems).catch(console.error);
  React.useEffect(() => { load(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.create('calibrations', form);
    setForm({ instrument: '', performed_by: '', reviewed_by: '', reference_used: '', scenario: '', measurements: '', uncertainty_calculation: '', result: '' });
    setShowForm(false);
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete?')) return;
    await api.remove('calibrations', id);
    load();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Calibrations</h1>
        <button onClick={() => setShowForm(!showForm)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
          {showForm ? 'Cancel' : '+ New'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-xl border space-y-3">
          <input name="instrument" placeholder="instrument" type="text" value={form.instrument || ""} onChange={e => setForm({...form, instrument: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="performed_by" placeholder="performed_by" type="text" value={form.performed_by || ""} onChange={e => setForm({...form, performed_by: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="reviewed_by" placeholder="reviewed_by" type="text" value={form.reviewed_by || ""} onChange={e => setForm({...form, reviewed_by: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="reference_used" placeholder="reference_used" type="text" value={form.reference_used || ""} onChange={e => setForm({...form, reference_used: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="scenario" placeholder="scenario" type="text" value={form.scenario || ""} onChange={e => setForm({...form, scenario: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="measurements" placeholder="measurements" type="text" value={form.measurements || ""} onChange={e => setForm({...form, measurements: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="uncertainty_calculation" placeholder="uncertainty_calculation" type="text" value={form.uncertainty_calculation || ""} onChange={e => setForm({...form, uncertainty_calculation: e.target.value})} className="border rounded px-3 py-2 text-sm" />
  <input name="result" placeholder="result" type="text" value={form.result || ""} onChange={e => setForm({...form, result: e.target.value})} className="border rounded px-3 py-2 text-sm" />
          <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Save</button>
        </form>
      )}

      <div className="bg-white rounded-xl border overflow-x-auto">
        <table className="w-full">
          <thead className="border-b"><tr><th className="text-left p-2 text-xs text-gray-500 uppercase">id</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">instrument</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">performed_by</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">reviewed_by</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">reference_used</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">scenario</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">date</th> <th className="text-left p-2 text-xs text-gray-500 uppercase">measurements</th><th></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 text-sm">{String(item.id ?? "")}</td> <td className="p-2 text-sm">{String(item.instrument ?? "")}</td> <td className="p-2 text-sm">{String(item.performed_by ?? "")}</td> <td className="p-2 text-sm">{String(item.reviewed_by ?? "")}</td> <td className="p-2 text-sm">{String(item.reference_used ?? "")}</td> <td className="p-2 text-sm">{String(item.scenario ?? "")}</td> <td className="p-2 text-sm">{String(item.date ?? "")}</td> <td className="p-2 text-sm">{String(item.measurements ?? "")}</td>
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
