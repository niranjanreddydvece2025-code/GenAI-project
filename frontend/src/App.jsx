import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";
import ChatbotPage from "./pages/ChatbotPage.jsx";
import EmployeeProfilePage from "./pages/EmployeeProfilePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import ShortlistPage from "./pages/ShortlistPage.jsx";
import UploadResumePage from "./pages/UploadResumePage.jsx";

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<ChatbotPage />} />
        <Route path="employee/:id" element={<EmployeeProfilePage />} />
        <Route path="shortlist" element={<ShortlistPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="upload" element={<UploadResumePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
