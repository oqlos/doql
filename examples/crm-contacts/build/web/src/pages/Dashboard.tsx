        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('contacts').then((d: any[]) => setCounts(c => ({...c, 'contacts': d.length})));
      api.list('companys').then((d: any[]) => setCounts(c => ({...c, 'companys': d.length})));
      api.list('deals').then((d: any[]) => setCounts(c => ({...c, 'deals': d.length})));
      api.list('activitys').then((d: any[]) => setCounts(c => ({...c, 'activitys': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">CRM Contacts</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/contacts" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Contacts</h3>
  <p className="text-2xl font-bold mt-1">{counts['contacts'] ?? '…'}</p>
</Link>
<Link to="/companys" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Companys</h3>
  <p className="text-2xl font-bold mt-1">{counts['companys'] ?? '…'}</p>
</Link>
<Link to="/deals" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Deals</h3>
  <p className="text-2xl font-bold mt-1">{counts['deals'] ?? '…'}</p>
</Link>
<Link to="/activitys" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Activitys</h3>
  <p className="text-2xl font-bold mt-1">{counts['activitys'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
