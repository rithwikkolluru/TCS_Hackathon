import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { AlertProvider } from "./context/AlertContext";
import ProtectedRoute from "./layouts/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";

// Pages
import Login from "./pages/Login";
import ManagerDashboard from "./pages/ManagerDashboard";
import EmployeeDashboard from "./pages/EmployeeDashboard";
import RegionalDashboard from "./pages/RegionalDashboard";
import BranchOverview from "./pages/BranchOverview";
import ServiceLoad from "./pages/ServiceLoad";
import Staffing from "./pages/Staffing";
import Bottlenecks from "./pages/Bottlenecks";
import Recommendations from "./pages/Recommendations";
import Feedback from "./pages/Feedback";
import Alerts from "./pages/Alerts";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

// Root Redirect component to direct user based on active role
const RootRedirect = () => {
  const { user, role, isAuthenticated, loading } = useAuth();

  if (loading) return null;
  if (!isAuthenticated()) return <Navigate to="/login" replace />;

  if (role === "manager") return <Navigate to="/manager" replace />;
  if (role === "employee") return <Navigate to="/employee" replace />;
  if (role === "regional_ops") return <Navigate to="/regional" replace />;

  return <Navigate to="/manager" replace />;
};

function App() {
  return (
    <AuthProvider>
      <AlertProvider>
        <Routes>
          {/* Public Auth Route */}
          <Route path="/login" element={<Login />} />

          {/* Root dynamic redirect */}
          <Route path="/" element={<RootRedirect />} />

          {/* Authenticated Application Layout */}
          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            {/* Manager View */}
            <Route
              path="/manager"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <ManagerDashboard />
                </ProtectedRoute>
              }
            />

            {/* Employee View */}
            <Route
              path="/employee"
              element={
                <ProtectedRoute allowedRoles={["employee", "manager", "regional_ops"]}>
                  <EmployeeDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/employee/tasks"
              element={
                <ProtectedRoute allowedRoles={["employee", "manager", "regional_ops"]}>
                  <EmployeeDashboard />
                </ProtectedRoute>
              }
            />

            {/* Regional Operations Views */}
            <Route
              path="/regional"
              element={
                <ProtectedRoute allowedRoles={["regional_ops"]}>
                  <RegionalDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/branches"
              element={
                <ProtectedRoute allowedRoles={["regional_ops"]}>
                  <RegionalDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/branches/:branchId"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <BranchOverview />
                </ProtectedRoute>
              }
            />

            {/* Functional Operational Pages */}
            <Route path="/service-load" element={<ServiceLoad />} />
            <Route
              path="/staffing"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <Staffing />
                </ProtectedRoute>
              }
            />
            <Route
              path="/bottlenecks"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <Bottlenecks />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/feedback"
              element={
                <ProtectedRoute allowedRoles={["manager", "regional_ops"]}>
                  <Feedback />
                </ProtectedRoute>
              }
            />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/profile" element={<Profile />} />
          </Route>

          {/* 404 Catch-All */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;
