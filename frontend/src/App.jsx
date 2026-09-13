import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Collections from "./pages/Collections";
import CollectionDetail from "./pages/CollectionDetail";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/collections"
        element={
          <ProtectedRoute>
            <Layout>
              <Collections />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/collections/:id"
        element={
          <ProtectedRoute>
            <Layout>
              <CollectionDetail />
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}