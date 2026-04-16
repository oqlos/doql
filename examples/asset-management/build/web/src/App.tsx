import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import StationPage from './pages/StationPage';
import OperatorPage from './pages/OperatorPage';
import QualificationPage from './pages/QualificationPage';
import DevicePage from './pages/DevicePage';
import InspectionPage from './pages/InspectionPage';
import CylinderFillPage from './pages/CylinderFillPage';
import ExercisePage from './pages/ExercisePage';
import DeploymentPage from './pages/DeploymentPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/stations" element={<StationPage />} />
        <Route path="/operators" element={<OperatorPage />} />
        <Route path="/qualifications" element={<QualificationPage />} />
        <Route path="/devices" element={<DevicePage />} />
        <Route path="/inspections" element={<InspectionPage />} />
        <Route path="/cylinder-fills" element={<CylinderFillPage />} />
        <Route path="/exercises" element={<ExercisePage />} />
        <Route path="/deployments" element={<DeploymentPage />} />
      </Route>
    </Routes>
  );
}
