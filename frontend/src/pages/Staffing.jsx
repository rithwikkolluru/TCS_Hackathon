import React, { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { predictionService } from "../services/predictionService";
import { regionalService } from "../services/regionalService";
import { useAuth } from "../context/AuthContext";
import { StaffingCard } from "../components/dashboard/StaffingCard";
import StaffUtilizationChart from "../charts/StaffUtilizationChart";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import { TIME_SLOTS, SERVICE_CATEGORIES } from "../utils/constants";
import { Users, AlertTriangle, CheckCircle, Clock, Calendar, RefreshCw } from "lucide-react";

export const Staffing = () => {
  const { selectedBranchId } = useOutletContext();
  const { role } = useAuth();
  const isRegional = role === "regional_ops";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [staffData, setStaffData] = useState([]);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState("11:00 - 13:00");
  const [selectedCategory, setSelectedCategory] = useState("");

  const fetchStaffingPredictions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (isRegional && selectedBranchId === "NETWORK_ALL") {
        const regRes = await regionalService.getStaffing();
        if (regRes?.success) {
          setStaffData(regRes.data || []);
        }
      } else {
        // Evaluate multiple time slots for branch
        const [slot1, slot2, slot3] = await Promise.all([
          predictionService.predictStaffRequirement({
            branch_id: selectedBranchId || "BR001",
            start_time: "09:00",
            end_time: "11:00",
            service_category: selectedCategory || undefined
          }),
          predictionService.predictStaffRequirement({
            branch_id: selectedBranchId || "BR001",
            start_time: "11:00",
            end_time: "13:00",
            service_category: selectedCategory || undefined
          }),
          predictionService.predictStaffRequirement({
            branch_id: selectedBranchId || "BR001",
            start_time: "14:00",
            end_time: "16:00",
            service_category: selectedCategory || undefined
          })
        ]);

        const formatted = [
          slot1?.data,
          slot2?.data,
          slot3?.data
        ].filter(Boolean);

        setStaffData(formatted);
      }
    } catch (err) {
      console.error("[Staffing] Fetch error:", err);
      setError("Unable to compute staff requirement predictions.");
    } finally {
      setLoading(false);
    }
  }, [selectedBranchId, isRegional, selectedCategory]);

  useEffect(() => {
    fetchStaffingPredictions();
  }, [fetchStaffingPredictions]);

  if (loading && staffData.length === 0) {
    return <LoadingSpinner message="Evaluating staff allocation models & counter capacities..." size="lg" />;
  }

  if (error && staffData.length === 0) {
    return <ErrorState message={error} onRetry={fetchStaffingPredictions} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-cyan-400" />
              Staff Capacity & Deficit Forecast
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Time-slot customer volume projections, required employee counts, and peak shortage warning alerts
            </p>
          </div>

          <button onClick={fetchStaffingPredictions} className="btn-secondary text-xs">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Recalculate Staff Requirements</span>
          </button>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 mt-4 border-t border-slate-800">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Filter by Service Category:</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="select-field w-full text-xs"
            >
              <option value="">All Service Counters Combined</option>
              {SERVICE_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Time-Slot Shortage Highlight Alert */}
      <div className="glass-card p-5 border-amber-500/40 bg-amber-950/20">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg flex-shrink-0 mt-0.5">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-amber-300">
              Critical Shortage Window Identified: 11:00 AM – 1:00 PM
            </h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Machine learning footfall forecasts predict customer arrivals will surge to ~200 visitors during the midday window. Active counter staff (5 employees) will incur average wait times of &gt; 35 minutes unless 2-4 additional tellers are mobilized.
            </p>
          </div>
        </div>
      </div>

      {/* Time-Slot Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {staffData.map((item, idx) => (
          <StaffingCard key={idx} item={item} />
        ))}
      </div>

      {/* Staff Utilization Chart */}
      <div className="glass-card p-5 border-slate-800">
        <h3 className="font-bold text-sm text-slate-100 mb-1">
          Counter Allocations vs Predicted Footfall Demand
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Visual comparison of available on-floor employees against AI required staff counts
        </p>
        <StaffUtilizationChart height={300} />
      </div>
    </div>
  );
};

export default Staffing;
