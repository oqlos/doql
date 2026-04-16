import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import NodePage from './pages/NodePage';
import TelemetryPage from './pages/TelemetryPage';
import DeploymentPage from './pages/DeploymentPage';
import FirmwareBuildPage from './pages/FirmwareBuildPage';
import OTAUpdatePage from './pages/OTAUpdatePage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/nodes" element={<NodePage />} />
        <Route path="/telemetrys" element={<TelemetryPage />} />
        <Route path="/deployments" element={<DeploymentPage />} />
        <Route path="/firmware-builds" element={<FirmwareBuildPage />} />
        <Route path="/ota-updates" element={<OTAUpdatePage />} />
      </Route>
    </Routes>
  );
}
