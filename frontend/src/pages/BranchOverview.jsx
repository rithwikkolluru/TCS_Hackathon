import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { dashboardService } from "../services/dashboardService";
import { recommendationService } from "../services/recommendationService";
import { feedbackService } from "../services/feedbackService";
import { branchService } from "../services/branchService";

import KpiCard from "../components/common/KpiCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import TrafficChart from "../charts/TrafficChart";
import HourlyTrafficChart from "../charts/HourlyTrafficChart";
import FeedbackChart from "../charts/FeedbackChart";
import ServiceLoadTable from "../components/dashboard/ServiceLoadTable";
import BottleneckCard from "../components/dashboard/BottleneckCard";
import RecommendationCard from "../components/dashboard/RecommendationCard";
import { formatNumber, formatMinutes } from "../utils/formatters";
import { BRANCHES } from "../utils/constants";

import {
  Building2,
  Users,
  Clock,
  Activity,
  ArrowLeft,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  MapPin,
  RefreshCw
} from "lucide-react";

export const BranchOverview = () => {
  const { branchId = "BR001" } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [bottlenecks, setBottlenecks] = useState([]);
  const [serviceLoad, setServiceLoad] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [branchDetail, setBranchDetail] = useState(null);

  const currentBranchMeta = BRANCHES.find((b) => b.branch_id === branchId) || {
    branch_id: branchId,
    branch_name: `${branchId} Branch`,
    city: "Telangana"
  };

  const fetchBranchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [sumRes, botRes, srvRes, recRes, fbkRes, bDetailRes] = await Promise.all([
        dashboardService.getSummary(branchId),
        dashboardService.getBottlenecks(branchId),
        dashboardService.getServiceLoad(branchId),
        recommendationService.getRecommendations(branchId),
        feedbackService.getFeedbackSummary(branchId),
        branchService.getBranch(branchId).catch(() => null)
      ]);

      if (sumRes?.success) setSummary(sumRes.data);
      if (botRes?.success) setBottlenecks(botRes.data || []);
      if (srvRes?.success) setServiceLoad(srvRes.data || []);
      if (recRes?.success) setRecommendations(recRes.data || []);
      if (fbkRes?.success) setFeedback(fbkRes.data);
      if (bDetailRes?.success) setBranchDetail(bDetailRes.data);
    } catch (err) {
      console.error("[BranchOverview] Fetch error:", err);
      setError("Unable to load branch details from backend.");
    } finally {
      setLoading(false);
    }
  }, [branchId]);

  useEffect(() => {
    fetchBranchData();
  }, [fetchBranchData]);

  if (loading && !summary) {
    return <LoadingSpinner message={`Loading telemetry for branch ${branchId}...`} size="lg" />;
  }

  if (error && !summary) {
    return <ErrorState message={error} onRetry={fetchBranchData} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-5 border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            title="Go back"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-cyan-400 font-mono">
                {branchId}
              </span>
              <span className="text-slate-500">•</span>
              <span className="text-xs text-slate-400">
                {currentBranchMeta.city}, {currentBranchMeta.state}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white mt-0.5">
              {currentBranchMeta.branch_name}
            </h1>
          </div>
        </div>

        <button onClick={fetchBranchData} className="btn-secondary text-xs">
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KpiCard
          title="Current Queue"
          value={summary?.current_queue || 28}
          subtitle="Waiting in Lobby"
          icon={Activity}
          accent="amber"
          risk={(summary?.current_queue || 28) > 20 ? "HIGH" : "LOW"}
        />
        <KpiCard
          title="Average Wait"
          value={formatMinutes(summary?.average_wait || 18.4)}
          subtitle="Target < 15m"
          icon={Clock}
          accent="cyan"
        />
        <KpiCard
          title="Predicted Daily Footfall"
          value={formatNumber(summary?.predicted_traffic || 210)}
          subtitle="Machine Learning"
          icon={TrendingUp}
          accent="indigo"
        />
        <KpiCard
          title="Active Bottlenecks"
          value={bottlenecks.filter((b) => b.risk_level === "HIGH" || b.risk_level === "CRITICAL").length}
          subtitle="High Risk Areas"
          icon={AlertTriangle}
          accent="rose"
          risk={bottlenecks.length > 0 ? "HIGH" : "LOW"}
        />
      </div>

      {/* Traffic Forecast Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-2">Footfall Traffic Forecast</h3>
          <TrafficChart height={260} />
        </div>
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-2">Hourly Surge Profile (8 AM - 5 PM)</h3>
          <HourlyTrafficChart height={260} />
        </div>
      </div>

      {/* Service Load Matrix */}
      <div className="glass-card p-5 border-slate-800">
        <h3 className="font-bold text-sm text-slate-100 mb-3">Service Category Breakdown</h3>
        <ServiceLoadTable items={serviceLoad} />
      </div>

      {/* Bottlenecks & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            Detected Service Bottlenecks
          </h3>
          <div className="space-y-3">
            {bottlenecks.map((b, idx) => (
              <BottleneckCard key={idx} item={b} />
            ))}
          </div>
        </div>

        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            Active AI Recommendations
          </h3>
          <div className="space-y-3">
            {recommendations.slice(0, 3).map((rec) => (
              <RecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BranchOverview;
