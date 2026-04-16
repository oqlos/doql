        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('notebooks').then((d: any[]) => setCounts(c => ({...c, 'notebooks': d.length})));
      api.list('notes').then((d: any[]) => setCounts(c => ({...c, 'notes': d.length})));
      api.list('tags').then((d: any[]) => setCounts(c => ({...c, 'tags': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">Notes</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/notebooks" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Notebooks</h3>
  <p className="text-2xl font-bold mt-1">{counts['notebooks'] ?? '…'}</p>
</Link>
<Link to="/notes" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Notes</h3>
  <p className="text-2xl font-bold mt-1">{counts['notes'] ?? '…'}</p>
</Link>
<Link to="/tags" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Tags</h3>
  <p className="text-2xl font-bold mt-1">{counts['tags'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
