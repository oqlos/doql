import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, List, Menu, X } from 'lucide-react';

const NAV = [
  { path: '/', label: 'Dashboard', icon: 'LayoutDashboard' },
];

const icons: Record<string, React.ElementType> = { LayoutDashboard, List };

export default function Layout() {
  const location = useLocation();
  const [open, setOpen] = React.useState(false);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className={`${open ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 fixed md:static z-30 w-64 h-full bg-white border-r transition-transform`}>
        <div className="p-4 border-b font-bold text-lg">Calibration Certificate Generator</div>
        <nav className="p-2 space-y-1">
          {NAV.map((item) => {
            const Icon = icons[item.icon] || List;
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${active ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="md:hidden flex items-center gap-3 p-3 border-b bg-white">
          <button onClick={() => setOpen(!open)}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="font-semibold">Calibration Certificate Generator</span>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
