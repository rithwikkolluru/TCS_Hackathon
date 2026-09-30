import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { useAlerts } from "../context/AlertContext";
import usePolling from "../hooks/usePolling";
import { dashboardService } from "../services/dashboardService";
import { branchService } from "../services/branchService";

import KpiCard from "../components/common/KpiCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import OperationalTasksCard from "../components/employee/OperationalTasksCard";
import CounterStatusCard from "../components/employee/CounterStatusCard";
import ServiceLoadTable from "../components/dashboard/ServiceLoadTable";
import AlertPanel from "../components/dashboard/AlertPanel";
import { formatNumber, formatMinutes } from "../utils/formatters";

import {
  Users,
  Clock,
  Activity,
  UserCheck,
  Building2,
  RefreshCw,
  Radio,
  CheckCircle2,
  Briefcase
} from "lucide-react";

export const EmployeeDashboard = () => {
  const { user } = useAuth();
  const { lastSurgeTimestamp } = useAlerts();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [serviceLoad, setServiceLoad] = useState([]);
  const [staffInfo, setStaffInfo] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const branchCode = user?.branch_id || "BR001";

  const fetchEmployeeData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    setError(null);

    try {
      const [sumRes, srvRes, stfRes] = await Promise.all([
        dashboardService.getSummary(branchCode),
        dashboardService.getServiceLoad(branchCode),
        branchService.getBranchStaff(branchCode)
      ]);

      if (sumRes?.success) setSummary(sumRes.data);
      if (srvRes?.success) setServiceLoad(srvRes.data || []);
      if (stfRes?.success) setStaffInfo(stfRes.data || []);
    } catch (err) {
      console.error("[EmployeeDashboard] Fetch error:", err);
      setError("Unable to load counter operations data. Please check connection.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [branchCode]);

  useEffect(() => {
    fetchEmployeeData();
  }, [fetchEmployeeData]);

  // Reactive refresh when surge happens
  useEffect(() => {
    if (lastSurgeTimestamp) {
      fetchEmployeeData(true);
    }
  }, [lastSurgeTimestamp, fetchEmployeeData]);

  usePolling(() => {
    fetchEmployeeData(true);
  }, 30000);

  if (loading && !summary) {
    return <LoadingSpinner message="Loading counter operations..." size="lg" />;
  }

  if (error && !summary) {
    return <ErrorState message={error} onRetry={() => fetchEmployeeData()} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-5 border-slate-800 bg-gradient-to-r from-slate-900/90 to-slate-950">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-cyan-400 font-mono">
              BRANCH: {branchCode}
            </span>
            <span className="text-slate-500">•</span>
            <span className="text-xs text-slate-400">Teller Terminal Station</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-white mt-1">
            Employee Workspace & Counter Operations
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Operational task board, real-time counter workload, and live branch surge telemetry
          </p>
        </div>

        <button
          onClick={() => {
            setRefreshing(true);
            fetchEmployeeData(true);
          }}
          disabled={refreshing}
          className="btn-secondary text-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
          <span>{refreshing ? "Refreshing..." : "Refresh Queue"}</span>
        </button>
      </div>

      {/* KPI Cards (Tailored for Employee Workload) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KpiCard
          title="Current Branch Queue"
          value={summary?.current_queue || 28}
          subtitle="Waiting in Lobby"
          icon={Activity}
          accent="amber"
          risk={(summary?.current_queue || 28) > 20 ? "HIGH" : "LOW"}
        />
        <KpiCard
          title="Est. Customer Wait"
          value={formatMinutes(summary?.average_wait || 18.4)}
          subtitle="Avg Processing Window"
          icon={Clock}
          accent="cyan"
        />
        <KpiCard
          title="Available Staff"
          value={summary?.staff_available || 5}
          subtitle="Active On-Duty"
          icon={UserCheck}
          accent="emerald"
        />
        <KpiCard
          title="Branch Total Visits"
          value={formatNumber(summary?.total_customers || 180)}
          subtitle="Processed Today"
          icon={Users}
          accent="indigo"
        />
      </div>

      {/* Main Employee Work Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Counter Status + Operational Tasks */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Station Card */}
          <CounterStatusCard staffInfo={staffInfo} branchName={branchCode} />

          {/* Operational Tasks (Dynamic AI Action Directives for Staff) */}
          <OperationalTasksCard />

          {/* Branch Service Load Summary */}
          <div className="glass-card p-5 border-slate-800">
            <h3 className="font-bold text-sm text-slate-100 mb-3">
              Branch Live Queue Workload (By Service)
            </h3>
            <ServiceLoadTable items={serviceLoad} />
          </div>
        </div>

        {/* Right Col: Live Operational Alerts */}
        <div className="space-y-6">
          <AlertPanel maxItems={5} showViewAll={true} />
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;
