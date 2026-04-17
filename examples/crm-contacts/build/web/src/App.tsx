import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ContactPage from './pages/ContactPage';
import CompanyPage from './pages/CompanyPage';
import DealPage from './pages/DealPage';
import ActivityPage from './pages/ActivityPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/contacts" element={<ContactPage />} />
        <Route path="/companys" element={<CompanyPage />} />
        <Route path="/deals" element={<DealPage />} />
        <Route path="/activitys" element={<ActivityPage />} />
      </Route>
    </Routes>
  );
}
