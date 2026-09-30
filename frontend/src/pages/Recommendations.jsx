import React, { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { recommendationService } from "../services/recommendationService";
import { useAlerts } from "../context/AlertContext";
import RecommendationCard from "../components/dashboard/RecommendationCard";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import { Lightbulb, Sparkles, Filter, RefreshCw, CheckCircle, Clock } from "lucide-react";

export const Recommendations = () => {
  const { selectedBranchId } = useOutletContext();
  const { addToast } = useAlerts();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [typeFilter, setTypeFilter] = useState("ALL");

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await recommendationService.getRecommendations(
        selectedBranchId || "BR001",
        statusFilter === "ALL" ? null : statusFilter
      );
      if (res?.success) {
        setRecommendations(res.data || []);
      }
    } catch (err) {
      console.error("[Recommendations] Fetch error:", err);
      setError("Unable to load recommendations from backend.");
    } finally {
      setLoading(false);
    }
  }, [selectedBranchId, statusFilter]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  const handleGenerate = async () => {
    try {
      const res = await recommendationService.generateRecommendations(selectedBranchId || "BR001");
      if (res?.success) {
        addToast({
          title: "AI ACTIONS GENERATED",
          message: `Generated ${res.data?.length || 0} recommendations for operational load leveling.`,
          riskLevel: "LOW",
          branch: selectedBranchId || "BR001"
        });
        fetchRecommendations();
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to generate recommendations.");
    }
  };

  const handleAccept = async (id, payload) => {
    try {
      const res = await recommendationService.acceptRecommendation(id, payload);
      if (res?.success) {
        addToast({
          title: "RECOMMENDATION ACCEPTED",
          message: `Action #${id} approved and recorded.`,
          riskLevel: "LOW",
          branch: selectedBranchId || "BR001"
        });
        fetchRecommendations();
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to accept recommendation.");
    }
  };

  const handleReject = async (id, payload) => {
    try {
      const res = await recommendationService.rejectRecommendation(id, payload);
      if (res?.success) {
        addToast({
          title: "RECOMMENDATION REJECTED",
          message: `Action #${id} rejected. Feedback recorded for ML learning.`,
          riskLevel: "MEDIUM",
          branch: selectedBranchId || "BR001"
        });
        fetchRecommendations();
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to reject recommendation.");
    }
  };

  const filteredRecs = recommendations.filter((r) => {
    if (typeFilter !== "ALL" && r.recommendation_type !== typeFilter) return false;
    return true;
  });

  if (loading && recommendations.length === 0) {
    return <LoadingSpinner message="Evaluating prescriptive AI optimization recommendations..." size="lg" />;
  }

  if (error && recommendations.length === 0) {
    return <ErrorState message={error} onRetry={fetchRecommendations} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-cyan-400" />
              AI Recommendation Engine & Manager Approvals
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Prescriptive operational load leveling, digital nudges, appointment smoothing, and closed-loop feedback tracking
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={fetchRecommendations} className="btn-secondary text-xs">
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
            <button onClick={handleGenerate} className="btn-primary text-xs">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generate New Actions</span>
            </button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-4 mt-4 border-t border-slate-800">
          {/* Status Filters */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5" />
              Status:
            </span>
            {["ALL", "PENDING", "ACCEPTED", "REJECTED"].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  statusFilter === status
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                    : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          {/* Type Filters */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-semibold text-slate-400 mr-1">Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="select-field text-xs py-1 px-2.5"
            >
              <option value="ALL">All Recommendation Types</option>
              <option value="STAFFING">Staffing Deployments</option>
              <option value="DIGITAL_REDIRECTION">Digital Redirection</option>
              <option value="APPOINTMENT_NUDGE">Appointment Nudge</option>
              <option value="BOTTLENECK_ALERT">Bottleneck Alert</option>
            </select>
          </div>
        </div>
      </div>

      {/* Grid of Recommendation Cards */}
      {filteredRecs.length === 0 ? (
        <EmptyState
          icon={Lightbulb}
          title="No Recommendations Found"
          message="No recommendations match your current status and type filters. Click 'Generate New Actions' to analyze live branch telemetry."
          action={
            <button onClick={handleGenerate} className="btn-primary text-xs">
              <Sparkles className="w-3.5 h-3.5" />
              Generate Now
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecs.map((rec) => (
            <RecommendationCard
              key={rec.id}
              recommendation={rec}
              onAccept={handleAccept}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
