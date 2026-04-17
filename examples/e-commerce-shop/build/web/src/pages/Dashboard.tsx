        import React from 'react';
        import { Link } from 'react-router-dom';
        import { api } from '../api';

        export default function Dashboard() {
          const [counts, setCounts] = React.useState<Record<string, number>>({}); 

          React.useEffect(() => {
              api.list('products').then((d: any[]) => setCounts(c => ({...c, 'products': d.length})));
      api.list('customers').then((d: any[]) => setCounts(c => ({...c, 'customers': d.length})));
      api.list('orders').then((d: any[]) => setCounts(c => ({...c, 'orders': d.length})));
      api.list('cart-items').then((d: any[]) => setCounts(c => ({...c, 'cart-items': d.length})));
          }, []);

          return (
            <div>
              <h1 className="text-2xl font-bold mb-6">E-Commerce Shop</h1>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/products" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Products</h3>
  <p className="text-2xl font-bold mt-1">{counts['products'] ?? '…'}</p>
</Link>
<Link to="/customers" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Customers</h3>
  <p className="text-2xl font-bold mt-1">{counts['customers'] ?? '…'}</p>
</Link>
<Link to="/orders" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">Orders</h3>
  <p className="text-2xl font-bold mt-1">{counts['orders'] ?? '…'}</p>
</Link>
<Link to="/cart-items" className="block p-6 bg-white rounded-xl border hover:shadow-md transition-shadow">
  <h3 className="text-sm text-gray-500">CartItems</h3>
  <p className="text-2xl font-bold mt-1">{counts['cart-items'] ?? '…'}</p>
</Link>
              </div>
            </div>
          );
        }
