import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import NotebookPage from './pages/NotebookPage';
import NotePage from './pages/NotePage';
import TagPage from './pages/TagPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/notebooks" element={<NotebookPage />} />
        <Route path="/notes" element={<NotePage />} />
        <Route path="/tags" element={<TagPage />} />
      </Route>
    </Routes>
  );
}
