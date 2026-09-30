import React, { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { dashboardService } from "../services/dashboardService";
import { regionalService } from "../services/regionalService";
import { useAuth } from "../context/AuthContext";
import BottleneckCard from "../components/dashboard/BottleneckCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import { AlertTriangle, ShieldAlert, Filter, RefreshCw, Zap } from "lucide-react";

export const Bottlenecks = () => {
  const { selectedBranchId } = useOutletContext();
  const { role } = useAuth();
  const isRegional = role === "regional_ops";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bottlenecks, setBottlenecks] = useState([]);
  const [riskFilter, setRiskFilter] = useState("ALL");

  const fetchBottlenecks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (isRegional && selectedBranchId === "NETWORK_ALL") {
        const res = await regionalService.getBottlenecks();
        if (res?.success) setBottlenecks(res.data || []);
      } else {
        const res = await dashboardService.getBottlenecks(selectedBranchId || "BR001");
        if (res?.success) setBottlenecks(res.data || []);
      }
    } catch (err) {
      console.error("[Bottlenecks] Fetch error:", err);
      setError("Unable to evaluate service bottlenecks from backend.");
    } finally {
      setLoading(false);
    }
  }, [selectedBranchId, isRegional]);

  useEffect(() => {
    fetchBottlenecks();
  }, [fetchBottlenecks]);

  const filteredBottlenecks = bottlenecks.filter((b) => {
    if (riskFilter !== "ALL" && b.risk_level !== riskFilter) return false;
    return true;
  });

  if (loading && bottlenecks.length === 0) {
    return <LoadingSpinner message="Scanning 14 service queues for bottleneck anomalies..." size="lg" />;
  }

  if (error && bottlenecks.length === 0) {
    return <ErrorState message={error} onRetry={fetchBottlenecks} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              Service Bottleneck Detector & Root Cause Triage
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Machine Learning anomaly detection identifying high-risk queue spikes and under-resourced counters
            </p>
          </div>

          <button onClick={fetchBottlenecks} className="btn-secondary text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Rescan Bottlenecks</span>
          </button>
        </div>

        {/* Risk Filter Tabs */}
        <div className="flex items-center gap-2 pt-4 mt-4 border-t border-slate-800 flex-wrap">
          <span className="text-xs font-semibold text-slate-400 mr-2 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            Filter Tier:
          </span>
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((tier) => (
            <button
              key={tier}
              onClick={() => setRiskFilter(tier)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                riskFilter === tier
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                  : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Bottleneck Cards */}
      {filteredBottlenecks.length === 0 ? (
        <EmptyState
          icon={ShieldAlert}
          title="No Bottlenecks in this Tier"
          message="No active bottlenecks match your selected risk filter criteria."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBottlenecks.map((item, idx) => (
            <BottleneckCard key={idx} item={item} />
          ))}
        </div>
      )}
    </div>
  );
};

export default Bottlenecks;
