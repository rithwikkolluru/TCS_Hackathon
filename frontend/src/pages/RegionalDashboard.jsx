import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { regionalService } from "../services/regionalService";
import { useAlerts } from "../context/AlertContext";
import usePolling from "../hooks/usePolling";

import KpiCard from "../components/common/KpiCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import RiskBadge from "../components/common/RiskBadge";
import AlertPanel from "../components/dashboard/AlertPanel";
import { formatNumber, formatMinutes } from "../utils/formatters";
import { BRANCHES } from "../utils/constants";

import {
  Building2,
  Users,
  TrendingUp,
  AlertTriangle,
  Clock,
  UserX,
  MapPin,
  ArrowRight,
  Globe2,
  RefreshCw,
  ExternalLink
} from "lucide-react";

export const RegionalDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [branchesLoad, setBranchesLoad] = useState([]);
  const [staffingList, setStaffingList] = useState([]);
  const [bottlenecks, setBottlenecks] = useState([]);
  const [selectedMapBranch, setSelectedMapBranch] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  const fetchRegionalData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    setError(null);

    try {
      const [loadRes, staffRes, botRes] = await Promise.all([
        regionalService.getLoad(),
        regionalService.getStaffing(),
        regionalService.getBottlenecks()
      ]);

      if (loadRes?.success) setBranchesLoad(loadRes.data || []);
      if (staffRes?.success) setStaffingList(staffRes.data || []);
      if (botRes?.success) setBottlenecks(botRes.data || []);

      if (loadRes?.data && loadRes.data.length > 0 && !selectedMapBranch) {
        setSelectedMapBranch(loadRes.data[0]);
      }
    } catch (err) {
      console.error("[RegionalDashboard] Fetch error:", err);
      setError("Unable to load regional network telemetry from backend.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [selectedMapBranch]);

  useEffect(() => {
    fetchRegionalData();
  }, [fetchRegionalData]);

  usePolling(() => {
    fetchRegionalData(true);
  }, 30000);

  if (loading && branchesLoad.length === 0) {
    return <LoadingSpinner message="Aggregating regional multi-branch operations..." size="lg" />;
  }

  if (error && branchesLoad.length === 0) {
    return <ErrorState message={error} onRetry={() => fetchRegionalData()} />;
  }

  // Network aggregates
  const totalBranches = branchesLoad.length || 8;
  const totalPredictedCustomers = branchesLoad.reduce((acc, b) => acc + (b.predicted_traffic || 0), 0) || 1450;
  const branchesAtRisk = branchesLoad.filter((b) => b.risk_level === "HIGH" || b.risk_level === "CRITICAL").length;
  const totalStaffShortage = staffingList.reduce((acc, s) => acc + (s.staff_gap || 0), 0);
  const networkAvgWait = branchesLoad.length
    ? (branchesLoad.reduce((acc, b) => acc + (b.average_wait_minutes || 0), 0) / branchesLoad.length).toFixed(1)
    : 16.5;

  const handleBranchClick = (branchId) => {
    navigate(`/branches/${branchId}`);
  };

  return (
    <div className="space-y-6">
      {/* Regional Operations Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-5 border-slate-800 bg-gradient-to-r from-slate-900/90 via-slate-900 to-slate-950">
        <div>
          <div className="flex items-center gap-2">
            <Globe2 className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-cyan-400 font-mono">
              REGIONAL OPERATIONS DIRECTORY (TELANGANA & ANDHRA PRADESH)
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-white mt-1">
            Network Operations Command Center
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Holistic cross-branch footfall balancing, capacity shortfall allocation & network bottleneck triage
          </p>
        </div>

        <button
          onClick={() => {
            setRefreshing(true);
            fetchRegionalData(true);
          }}
          disabled={refreshing}
          className="btn-secondary text-xs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
          <span>{refreshing ? "Syncing Network..." : "Refresh Network"}</span>
        </button>
      </div>

      {/* 5 Regional Overview KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Total Branches"
          value={totalBranches}
          subtitle="Operational Network"
          icon={Building2}
          accent="cyan"
        />
        <KpiCard
          title="Total Pred. Traffic"
          value={formatNumber(totalPredictedCustomers)}
          subtitle="Network Daily Volume"
          icon={TrendingUp}
          accent="indigo"
        />
        <KpiCard
          title="Branches at Risk"
          value={branchesAtRisk}
          subtitle="HIGH / CRITICAL"
          icon={AlertTriangle}
          risk={branchesAtRisk > 0 ? "HIGH" : "LOW"}
          accent="rose"
          highlight={branchesAtRisk > 0}
        />
        <KpiCard
          title="Total Staff Shortage"
          value={`-${totalStaffShortage}`}
          subtitle="Peak Slot Deficit"
          icon={UserX}
          accent="amber"
        />
        <KpiCard
          title="Network Avg Wait"
          value={`${networkAvgWait}m`}
          subtitle="SLA Baseline: 15.0m"
          icon={Clock}
          accent="emerald"
        />
      </div>

      {/* Interactive Geographic Map Visualization + Selected Branch Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Branch Network Map Grid */}
        <div className="lg:col-span-2 glass-card p-5 border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-cyan-400" />
                Regional Geographic Branch Distribution & Telemetry
              </h3>
              <p className="text-xs text-slate-400">
                Click any branch node to inspect live traffic, queue length, waiting time, and staffing metrics
              </p>
            </div>
          </div>

          {/* Interactive Geographic Node Map */}
          <div className="relative w-full h-80 bg-slate-950 rounded-xl border border-slate-800/80 p-4 overflow-hidden flex flex-col justify-between">
            {/* Background Grid Lines */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-20 pointer-events-none" />

            {/* Geographical Cards Grid representing Telangana & AP branches */}
            <div className="relative z-10 grid grid-cols-2 sm:grid-cols-4 gap-2.5 h-full">
              {branchesLoad.map((b) => {
                const isSelected = selectedMapBranch?.branch_id === b.branch_id;
                const isCrit = b.risk_level === "HIGH" || b.risk_level === "CRITICAL";

                return (
                  <div
                    key={b.branch_id}
                    onClick={() => setSelectedMapBranch(b)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                      isSelected
                        ? "bg-cyan-950/50 border-cyan-400 ring-2 ring-cyan-500/40 shadow-xl"
                        : isCrit
                        ? "bg-rose-950/20 border-rose-500/40 hover:bg-rose-950/30"
                        : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div>
                      <div className="flex items-start justify-between gap-1 mb-1">
                        <span className="font-mono text-[10px] text-cyan-400 font-bold">{b.branch_id}</span>
                        <RiskBadge risk={b.risk_level} size="sm" />
                      </div>
                      <h4 className="font-bold text-xs text-slate-100 line-clamp-1">{b.branch_name}</h4>
                      <p className="text-[10px] text-slate-400">{b.city}</p>
                    </div>

                    <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                      <span className="text-slate-400">Queue:</span>
                      <span className="font-mono font-bold text-slate-100">{b.current_queue}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Branch Drill-down Inspector */}
        <div className="space-y-6">
          {selectedMapBranch ? (
            <div className="glass-card p-5 border-cyan-500/30 bg-slate-900">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase">
                  Active Inspector Node
                </span>
                <RiskBadge risk={selectedMapBranch.risk_level} size="sm" />
              </div>

              <h3 className="font-bold text-base text-white">{selectedMapBranch.branch_name}</h3>
              <p className="text-xs text-slate-400">{selectedMapBranch.city} • Branch Code: {selectedMapBranch.branch_id}</p>

              <div className="grid grid-cols-2 gap-2 my-4 text-xs">
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Pred. Traffic</span>
                  <span className="font-mono font-bold text-sm text-cyan-400 block mt-0.5">
                    {selectedMapBranch.predicted_traffic} cust
                  </span>
                </div>
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Current Queue</span>
                  <span className="font-mono font-bold text-sm text-amber-400 block mt-0.5">
                    {selectedMapBranch.current_queue} in lobby
                  </span>
                </div>
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Average Wait</span>
                  <span className="font-mono font-bold text-sm text-rose-400 block mt-0.5">
                    {selectedMapBranch.average_wait_minutes}m
                  </span>
                </div>
                <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Staff Ratio</span>
                  <span className="font-mono font-bold text-sm text-emerald-400 block mt-0.5">
                    {selectedMapBranch.staff_available} / {selectedMapBranch.staff_required}
                  </span>
                </div>
              </div>

              <button
                onClick={() => handleBranchClick(selectedMapBranch.branch_id)}
                className="w-full btn-primary text-xs py-2 justify-between"
              >
                <span>Open Branch Detailed Analysis</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : null}

          {/* Network Alerts Quick View */}
          <AlertPanel maxItems={3} showViewAll={true} />
        </div>
      </div>

      {/* Cross-Branch Comparison Table */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-sm text-slate-100">Regional Branch Comparative Load Matrix</h3>
            <p className="text-xs text-slate-400">
              Live benchmark comparison across all 8 network branches with deep drill-down capabilities
            </p>
          </div>
        </div>

        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-semibold">
              <tr>
                <th className="py-3 px-4">Branch Code & Name</th>
                <th className="py-3 px-3">City</th>
                <th className="py-3 px-3 text-center">Predicted Traffic</th>
                <th className="py-3 px-3 text-center">Current Queue</th>
                <th className="py-3 px-3 text-center">Average Wait</th>
                <th className="py-3 px-3 text-center">Available Staff</th>
                <th className="py-3 px-3 text-center">Required Staff</th>
                <th className="py-3 px-3 text-center">Operational Risk</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {branchesLoad.map((b) => (
                <tr key={b.branch_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-semibold text-slate-200">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-cyan-400">{b.branch_id}</span>
                      <span className="text-slate-300 font-medium truncate">{b.branch_name}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-slate-400">{b.city}</td>
                  <td className="py-3 px-3 text-center font-mono font-bold text-slate-100">
                    {b.predicted_traffic}
                  </td>
                  <td className="py-3 px-3 text-center font-mono font-bold text-amber-400">
                    {b.current_queue}
                  </td>
                  <td className="py-3 px-3 text-center font-mono font-bold text-cyan-400">
                    {formatMinutes(b.average_wait_minutes)}
                  </td>
                  <td className="py-3 px-3 text-center font-mono text-emerald-400">
                    {b.staff_available}
                  </td>
                  <td className="py-3 px-3 text-center font-mono text-slate-300">
                    {b.staff_required}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <RiskBadge risk={b.risk_level} size="sm" />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleBranchClick(b.branch_id)}
                      className="btn-secondary text-[11px] py-1 px-2.5"
                    >
                      <span>Drilldown</span>
                      <ArrowRight className="w-3 h-3 text-cyan-400" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RegionalDashboard;
