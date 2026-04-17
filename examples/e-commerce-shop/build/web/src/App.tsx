import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ProductPage from './pages/ProductPage';
import CustomerPage from './pages/CustomerPage';
import OrderPage from './pages/OrderPage';
import CartItemPage from './pages/CartItemPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<ProductPage />} />
        <Route path="/customers" element={<CustomerPage />} />
        <Route path="/orders" element={<OrderPage />} />
        <Route path="/cart-items" element={<CartItemPage />} />
      </Route>
    </Routes>
  );
}
