import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import OperatorPage from './pages/OperatorPage';
import InstrumentPage from './pages/InstrumentPage';
import ReferenceStandardPage from './pages/ReferenceStandardPage';
import CalibrationPage from './pages/CalibrationPage';
import CustomerPage from './pages/CustomerPage';
import CalibrationOrderPage from './pages/CalibrationOrderPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/operators" element={<OperatorPage />} />
        <Route path="/instruments" element={<InstrumentPage />} />
        <Route path="/reference-standards" element={<ReferenceStandardPage />} />
        <Route path="/calibrations" element={<CalibrationPage />} />
        <Route path="/customers" element={<CustomerPage />} />
        <Route path="/calibration-orders" element={<CalibrationOrderPage />} />
      </Route>
    </Routes>
  );
}
