        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('posts').then((d: any[]) => setCounts(c => ({...c, 'posts': d.length})));
      api.list('authors').then((d: any[]) => setCounts(c => ({...c, 'authors': d.length})));
      api.list('categorys').then((d: any[]) => setCounts(c => ({...c, 'categorys': d.length})));
      api.list('comments').then((d: any[]) => setCounts(c => ({...c, 'comments': d.length})));
      api.list('media-files').then((d: any[]) => setCounts(c => ({...c, 'media-files': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">Blog CMS</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/posts" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Posts</h3>
  <p className="text-2xl font-bold mt-1">{counts['posts'] ?? '…'}</p>
</Link>
<Link to="/authors" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Authors</h3>
  <p className="text-2xl font-bold mt-1">{counts['authors'] ?? '…'}</p>
</Link>
<Link to="/categorys" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Categorys</h3>
  <p className="text-2xl font-bold mt-1">{counts['categorys'] ?? '…'}</p>
</Link>
<Link to="/comments" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Comments</h3>
  <p className="text-2xl font-bold mt-1">{counts['comments'] ?? '…'}</p>
</Link>
<Link to="/media-files" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">MediaFiles</h3>
  <p className="text-2xl font-bold mt-1">{counts['media-files'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
