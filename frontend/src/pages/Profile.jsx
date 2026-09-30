import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { auditService } from "../services/auditService";
import { formatDateTime } from "../utils/formatters";
import { Shield, User, Key, Building2, Lock, History, CheckCircle, Clock } from "lucide-react";

export const Profile = () => {
  const { user, role, logout } = useAuth();
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAudit = async () => {
      setLoading(true);
      try {
        const res = await auditService.getAuditLogs(null, 10);
        if (res?.success) {
          setAuditLogs(res.data || []);
        }
      } catch (err) {
        console.warn("[Profile] Audit log fetch:", err);
      } finally {
        setLoading(false);
      }
    };

    if (role === "manager" || role === "regional_ops") {
      fetchAudit();
    }
  }, [role]);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-2xl text-white shadow-lg">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Staff Profile & Access Security</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Authenticated banking credentials, role-based authorization parameters, and compliance audit trail
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* User Card */}
        <div className="glass-card p-5 border-slate-800 space-y-4">
          <div className="text-center pb-4 border-b border-slate-800">
            <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 text-cyan-400 font-extrabold text-2xl flex items-center justify-center mx-auto mb-3">
              {user?.name ? user.name[0] : "U"}
            </div>
            <h3 className="font-bold text-base text-slate-100">{user?.name || "Staff Member"}</h3>
            <p className="text-xs text-slate-400">{user?.email}</p>
            <span className="inline-block mt-2 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-mono uppercase font-bold">
              {role?.replace(/_/g, " ")}
            </span>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-400">Assigned Branch:</span>
              <span className="font-mono font-bold text-cyan-400">
                {user?.branch_id || "Network Wide (All Branches)"}
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/80">
              <span className="text-slate-400">Account Status:</span>
              <span className="font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" />
                Active Verified
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Security Standard:</span>
              <span className="font-mono text-slate-300">JWT RS256 Bearer</span>
            </div>
          </div>

          <button onClick={logout} className="w-full btn-danger text-xs py-2 mt-2">
            Terminate Active Session
          </button>
        </div>

        {/* Security & RBAC Specs */}
        <div className="md:col-span-2 space-y-6">
          <div className="glass-card p-5 border-slate-800">
            <h3 className="font-bold text-sm text-slate-100 mb-3 flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" />
              Role-Based Access Control (RBAC) Entitlements
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                <p className="font-bold text-slate-200">
                  Current Authorization Level: <span className="text-cyan-400 capitalize">{role}</span>
                </p>
                <p className="text-slate-400 mt-1 leading-relaxed">
                  {role === "manager"
                    ? "Permitted: Telemetry monitoring, recommendation generation, recommendation accept/reject sign-off, live surge injection, and staff roster oversight for assigned branch."
                    : role === "employee"
                    ? "Permitted: Counter queue processing, operational task updates, station workload metrics, and live branch alert notifications. (Manager approvals disabled)."
                    : "Permitted: Full network cross-branch analytics, geographic performance matrix, regional capacity allocations, and multi-branch bottleneck aggregation."}
                </p>
              </div>
            </div>
          </div>

          {/* Audit Logs Trail */}
          {(role === "manager" || role === "regional_ops") && (
            <div className="glass-card p-5 border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                  <History className="w-4 h-4 text-cyan-400" />
                  Recent Security & Audit Logs (Immutable)
                </h3>
              </div>

              <div className="space-y-2">
                {auditLogs.length === 0 ? (
                  <p className="text-xs text-slate-500 py-4 text-center">No recent audit records.</p>
                ) : (
                  auditLogs.map((log) => (
                    <div
                      key={log.id}
                      className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-mono font-bold text-cyan-400">{log.action}</span>
                        <span className="text-slate-400 ml-2 font-mono">
                          {log.resource} ({log.resource_id || "global"})
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {formatDateTime(log.timestamp)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
