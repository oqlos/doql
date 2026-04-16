        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('stations').then((d: any[]) => setCounts(c => ({...c, 'stations': d.length})));
      api.list('operators').then((d: any[]) => setCounts(c => ({...c, 'operators': d.length})));
      api.list('qualifications').then((d: any[]) => setCounts(c => ({...c, 'qualifications': d.length})));
      api.list('devices').then((d: any[]) => setCounts(c => ({...c, 'devices': d.length})));
      api.list('inspections').then((d: any[]) => setCounts(c => ({...c, 'inspections': d.length})));
      api.list('cylinder-fills').then((d: any[]) => setCounts(c => ({...c, 'cylinder-fills': d.length})));
      api.list('exercises').then((d: any[]) => setCounts(c => ({...c, 'exercises': d.length})));
      api.list('deployments').then((d: any[]) => setCounts(c => ({...c, 'deployments': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">Mask Inspection Manager</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/stations" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Stations</h3>
  <p className="text-2xl font-bold mt-1">{counts['stations'] ?? '…'}</p>
</Link>
<Link to="/operators" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Operators</h3>
  <p className="text-2xl font-bold mt-1">{counts['operators'] ?? '…'}</p>
</Link>
<Link to="/qualifications" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Qualifications</h3>
  <p className="text-2xl font-bold mt-1">{counts['qualifications'] ?? '…'}</p>
</Link>
<Link to="/devices" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Devices</h3>
  <p className="text-2xl font-bold mt-1">{counts['devices'] ?? '…'}</p>
</Link>
<Link to="/inspections" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Inspections</h3>
  <p className="text-2xl font-bold mt-1">{counts['inspections'] ?? '…'}</p>
</Link>
<Link to="/cylinder-fills" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">CylinderFills</h3>
  <p className="text-2xl font-bold mt-1">{counts['cylinder-fills'] ?? '…'}</p>
</Link>
<Link to="/exercises" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Exercises</h3>
  <p className="text-2xl font-bold mt-1">{counts['exercises'] ?? '…'}</p>
</Link>
<Link to="/deployments" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Deployments</h3>
  <p className="text-2xl font-bold mt-1">{counts['deployments'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
