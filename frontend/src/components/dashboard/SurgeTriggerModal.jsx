import React, { useState } from "react";
import { Zap, AlertTriangle, X, CheckCircle2 } from "lucide-react";
import { liveService } from "../../services/liveService";
import { SERVICE_CATEGORIES } from "../../utils/constants";
import { useAlerts } from "../../context/AlertContext";

export const SurgeTriggerModal = ({ isOpen, onClose, branchId = "BR001", onSurgeSuccess = null }) => {
  const [selectedService, setSelectedService] = useState("Withdrawal");
  const [loading, setLoading] = useState(false);
  const [surgeResult, setSurgeResult] = useState(null);
  const [error, setError] = useState(null);
  const { addToast } = useAlerts();

  if (!isOpen) return null;

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    setSurgeResult(null);

    try {
      const res = await liveService.simulateSurge(branchId, selectedService);
      if (res && res.success) {
        setSurgeResult(res.data);
        addToast({
          title: "CRITICAL SURGE INGESTED",
          message: res.explanation || `Surge triggered for ${selectedService} at ${branchId}`,
          riskLevel: "CRITICAL",
          branch: branchId,
          service: selectedService
        });

        if (onSurgeSuccess) {
          onSurgeSuccess(res.data);
        }
      } else {
        setError(res?.explanation || "Failed to trigger live surge simulation.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Network error while triggering surge simulation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="glass-card max-w-md w-full p-6 border-rose-500/40 bg-slate-900 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-200"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">Live Traffic Surge Simulator</h3>
            <p className="text-xs text-slate-400">
              Inject instantaneous 30-50 queue load to trigger WebSocket alerts
            </p>
          </div>
        </div>

        <div className="space-y-4 mb-5">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Branch:
            </label>
            <input
              type="text"
              value={branchId}
              disabled
              className="input-field text-xs bg-slate-950 font-mono text-cyan-400 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Service Category:
            </label>
            <select
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              className="select-field w-full text-xs"
            >
              {SERVICE_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <div className="p-3 bg-rose-950/40 border border-rose-500/40 rounded-lg text-xs text-rose-300 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {surgeResult && (
            <div className="p-3 bg-emerald-950/40 border border-emerald-500/40 rounded-lg text-xs text-emerald-300 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>Live Surge Ingested & Broadcasted!</span>
              </div>
              <p className="text-slate-300 text-[11px]">
                Queue Length: <span className="font-mono font-bold text-white">{surgeResult.queue_length}</span> | 
                Staff: <span className="font-mono font-bold text-rose-400">{surgeResult.staff_available}</span>
              </p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary text-xs"
          >
            Close
          </button>
          <button
            type="button"
            onClick={handleSimulate}
            disabled={loading}
            className="bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white px-4 py-2 rounded-lg text-xs font-bold transition-all shadow-lg flex items-center gap-2 disabled:opacity-50"
          >
            <Zap className="w-4 h-4" />
            {loading ? "Simulating Surge..." : "Trigger Live Surge Now"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SurgeTriggerModal;
