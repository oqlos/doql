import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PostPage from './pages/PostPage';
import AuthorPage from './pages/AuthorPage';
import CategoryPage from './pages/CategoryPage';
import CommentPage from './pages/CommentPage';
import MediaFilePage from './pages/MediaFilePage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/posts" element={<PostPage />} />
        <Route path="/authors" element={<AuthorPage />} />
        <Route path="/categorys" element={<CategoryPage />} />
        <Route path="/comments" element={<CommentPage />} />
        <Route path="/media-files" element={<MediaFilePage />} />
      </Route>
    </Routes>
  );
}
