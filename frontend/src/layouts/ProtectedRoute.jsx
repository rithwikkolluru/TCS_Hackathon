import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { ShieldAlert } from "lucide-react";

export const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, role, token, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <LoadingSpinner message="Authenticating banking session..." size="lg" />
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // RBAC permission check
  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6">
        <div className="glass-card max-w-md w-full p-8 text-center border-rose-500/40 bg-rose-950/20">
          <div className="p-3 bg-rose-500/20 text-rose-400 rounded-full w-14 h-14 mx-auto mb-4 flex items-center justify-center border border-rose-500/30">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-100">Access Restricted (403)</h2>
          <p className="text-sm text-slate-400 mt-2">
            Your role (<span className="text-cyan-400 font-mono font-bold capitalize">{role}</span>) does not have authorization to view this operational zone.
          </p>
          <div className="mt-6 flex flex-col gap-2">
            <Navigate to={role === "manager" ? "/manager" : role === "employee" ? "/employee" : "/regional"} replace />
          </div>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;
