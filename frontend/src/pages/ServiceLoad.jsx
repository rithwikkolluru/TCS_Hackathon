import React, { useState, useEffect, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { dashboardService } from "../services/dashboardService";
import { ServiceFilter } from "../components/common/ServiceFilter";
import { DateSelector } from "../components/common/DateSelector";
import ServiceLoadTable from "../components/dashboard/ServiceLoadTable";
import WaitTimeChart from "../charts/WaitTimeChart";
import StaffUtilizationChart from "../charts/StaffUtilizationChart";
import RiskDistributionChart from "../charts/RiskDistributionChart";
import TrafficChart from "../charts/TrafficChart";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import { BarChart3, Filter, RefreshCw, Layers } from "lucide-react";

export const ServiceLoad = () => {
  const { selectedBranchId } = useOutletContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [serviceLoad, setServiceLoad] = useState([]);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);

  const fetchServiceLoad = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await dashboardService.getServiceLoad(selectedBranchId);
      if (res?.success) {
        setServiceLoad(res.data || []);
      }
    } catch (err) {
      console.error("[ServiceLoad] Fetch error:", err);
      setError("Unable to load service load metrics from backend.");
    } finally {
      setLoading(false);
    }
  }, [selectedBranchId]);

  useEffect(() => {
    fetchServiceLoad();
  }, [fetchServiceLoad]);

  // Apply frontend filtering on the authoritative backend service load array
  const filteredItems = serviceLoad.filter((item) => {
    if (categoryFilter && item.service_category !== categoryFilter) return false;
    if (riskFilter !== "ALL" && item.risk_level !== riskFilter) return false;
    return true;
  });

  const waitChartData = filteredItems.map((item) => ({
    service: item.service_category.split(" ")[0],
    wait: item.predicted_wait,
    queue: item.queue_length,
    risk: item.risk_level
  }));

  const staffChartData = filteredItems.map((item) => ({
    category: item.service_category.split(" ")[0],
    available: item.staff_available,
    required: item.staff_required,
    gap: Math.max(0, item.staff_required - item.staff_available)
  }));

  const riskCounts = {
    low: serviceLoad.filter((s) => s.risk_level === "LOW").length,
    medium: serviceLoad.filter((s) => s.risk_level === "MEDIUM").length,
    high: serviceLoad.filter((s) => s.risk_level === "HIGH").length,
    critical: serviceLoad.filter((s) => s.risk_level === "CRITICAL").length
  };

  if (loading && serviceLoad.length === 0) {
    return <LoadingSpinner message="Calculating 14-service load distributions..." size="lg" />;
  }

  if (error && serviceLoad.length === 0) {
    return <ErrorState message={error} onRetry={fetchServiceLoad} />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-cyan-400" />
              Service Load & Queue Distribution Matrix
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Multi-dimensional analysis across all 14 banking services, wait times, staffing utilization, and risk thresholds
            </p>
          </div>

          <button onClick={fetchServiceLoad} className="btn-secondary text-xs self-start md:self-auto">
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reload Load Metrics</span>
          </button>
        </div>

        {/* Filter Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 border-t border-slate-800/80">
          <ServiceFilter
            selectedCategory={categoryFilter}
            onSelectCategory={setCategoryFilter}
          />
          <div>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="select-field w-full text-xs"
            >
              <option value="ALL">All Risk Tiers</option>
              <option value="CRITICAL">CRITICAL Only</option>
              <option value="HIGH">HIGH Only</option>
              <option value="MEDIUM">MEDIUM Only</option>
              <option value="LOW">LOW Only</option>
            </select>
          </div>
          <DateSelector
            selectedDate={selectedDate}
            onSelectDate={setSelectedDate}
          />
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Waiting Time Chart */}
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-1">Predicted Waiting Time vs SLA Limit (20m)</h3>
          <p className="text-xs text-slate-400 mb-3">Service categories color-coded by operational risk tier</p>
          <WaitTimeChart data={waitChartData} height={280} benchmark={20} />
        </div>

        {/* Staff Utilization Chart */}
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-1">Staff Deployment vs AI Required Capacity</h3>
          <p className="text-xs text-slate-400 mb-3">Identifies understaffed counter assignments across services</p>
          <StaffUtilizationChart data={staffChartData} height={280} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Traffic Chart */}
        <div className="lg:col-span-2 glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-1">Branch Footfall Volume Progression</h3>
          <p className="text-xs text-slate-400 mb-3">Historical arrival trends vs Machine Learning forecast</p>
          <TrafficChart height={240} />
        </div>

        {/* Risk Distribution Chart */}
        <div className="glass-card p-5 border-slate-800">
          <h3 className="font-bold text-sm text-slate-100 mb-1">Risk Profile Breakdown</h3>
          <p className="text-xs text-slate-400 mb-3">Distribution of 14 service risk states</p>
          <RiskDistributionChart
            low={riskCounts.low}
            medium={riskCounts.medium}
            high={riskCounts.high}
            critical={riskCounts.critical}
            height={220}
          />
        </div>
      </div>

      {/* Main Service Load Table */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold text-sm text-slate-100">
            Filtered Service Load Metrics ({filteredItems.length} Services)
          </h3>
        </div>
        <ServiceLoadTable items={filteredItems} />
      </div>
    </div>
  );
};

export default ServiceLoad;
