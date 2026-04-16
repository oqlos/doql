        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('nodes').then((d: any[]) => setCounts(c => ({...c, 'nodes': d.length})));
      api.list('telemetrys').then((d: any[]) => setCounts(c => ({...c, 'telemetrys': d.length})));
      api.list('deployments').then((d: any[]) => setCounts(c => ({...c, 'deployments': d.length})));
      api.list('firmware-builds').then((d: any[]) => setCounts(c => ({...c, 'firmware-builds': d.length})));
      api.list('ota-updates').then((d: any[]) => setCounts(c => ({...c, 'ota-updates': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">IoT Fleet Manager</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/nodes" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Nodes</h3>
  <p className="text-2xl font-bold mt-1">{counts['nodes'] ?? '…'}</p>
</Link>
<Link to="/telemetrys" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Telemetrys</h3>
  <p className="text-2xl font-bold mt-1">{counts['telemetrys'] ?? '…'}</p>
</Link>
<Link to="/deployments" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Deployments</h3>
  <p className="text-2xl font-bold mt-1">{counts['deployments'] ?? '…'}</p>
</Link>
<Link to="/firmware-builds" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">FirmwareBuilds</h3>
  <p className="text-2xl font-bold mt-1">{counts['firmware-builds'] ?? '…'}</p>
</Link>
<Link to="/ota-updates" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">OTAUpdates</h3>
  <p className="text-2xl font-bold mt-1">{counts['ota-updates'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
