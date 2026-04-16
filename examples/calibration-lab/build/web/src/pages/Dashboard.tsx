        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('instruments').then((d: any[]) => setCounts(c => ({...c, 'instruments': d.length})));
      api.list('reference-standards').then((d: any[]) => setCounts(c => ({...c, 'reference-standards': d.length})));
      api.list('calibrations').then((d: any[]) => setCounts(c => ({...c, 'calibrations': d.length})));
      api.list('customers').then((d: any[]) => setCounts(c => ({...c, 'customers': d.length})));
      api.list('calibration-orders').then((d: any[]) => setCounts(c => ({...c, 'calibration-orders': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">Calibration Lab Manager</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/instruments" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Instruments</h3>
  <p className="text-2xl font-bold mt-1">{counts['instruments'] ?? '…'}</p>
</Link>
<Link to="/reference-standards" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">ReferenceStandards</h3>
  <p className="text-2xl font-bold mt-1">{counts['reference-standards'] ?? '…'}</p>
</Link>
<Link to="/calibrations" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Calibrations</h3>
  <p className="text-2xl font-bold mt-1">{counts['calibrations'] ?? '…'}</p>
</Link>
<Link to="/customers" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Customers</h3>
  <p className="text-2xl font-bold mt-1">{counts['customers'] ?? '…'}</p>
</Link>
<Link to="/calibration-orders" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">CalibrationOrders</h3>
  <p className="text-2xl font-bold mt-1">{counts['calibration-orders'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
