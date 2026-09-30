import React from "react";
import RiskBadge from "../common/RiskBadge";
import { AlertCircle, Clock, Users, ArrowRight } from "lucide-react";

export const BottleneckCard = ({ item, onTakeAction = null }) => {
  if (!item) return null;

  const isCritical = item.risk_level === "CRITICAL";
  const isHigh = item.risk_level === "HIGH";

  return (
    <div
      className={`glass-card p-4 transition-all duration-200 ${
        isCritical
          ? "border-rose-500/50 bg-rose-950/20 shadow-lg shadow-rose-950/20"
          : isHigh
          ? "border-orange-500/40 bg-orange-950/15 shadow-lg shadow-orange-950/20"
          : "border-slate-800 hover:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2.5">
        <div className="flex items-center gap-2">
          <div
            className={`p-1.5 rounded-lg ${
              isCritical
                ? "bg-rose-500/20 text-rose-400"
                : isHigh
                ? "bg-orange-500/20 text-orange-400"
                : "bg-cyan-500/20 text-cyan-400"
            }`}
          >
            <AlertCircle className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-sm text-slate-100 line-clamp-1">
            {item.service_category}
          </h4>
        </div>
        <RiskBadge risk={item.risk_level} size="sm" />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 my-3 text-center">
        <div>
          <span className="text-[10px] text-slate-400 block uppercase font-medium">Queue</span>
          <span className="font-mono font-bold text-sm text-slate-100">{item.queue_length}</span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 block uppercase font-medium">Pred. Wait</span>
          <span className="font-mono font-bold text-sm text-cyan-400">
            {Number(item.predicted_wait_minutes).toFixed(1)}m
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 block uppercase font-medium">Staff (Av/Req)</span>
          <span className="font-mono font-bold text-sm text-amber-400">
            {item.staff_available} / {item.staff_required}
          </span>
        </div>
      </div>

      {/* Structured AI Explanation (Requirement 20: Prediction + Reason + Action) */}
      <div className="space-y-1.5 text-xs border-t border-slate-800/80 pt-2.5 text-slate-300">
        <div className="flex items-start gap-1.5">
          <span className="font-semibold text-cyan-400 flex-shrink-0">Prediction:</span>
          <span className="text-slate-300">
            Queue length {item.queue_length} with ~{Number(item.predicted_wait_minutes).toFixed(1)} min wait time.
          </span>
        </div>
        <div className="flex items-start gap-1.5">
          <span className="font-semibold text-amber-400 flex-shrink-0">Reason:</span>
          <span className="text-slate-400 italic">
            {item.explanation || "Footfall spike causing counter processing delay."}
          </span>
        </div>
        <div className="flex items-start gap-1.5">
          <span className="font-semibold text-emerald-400 flex-shrink-0">Action:</span>
          <span className="text-slate-300">
            Deploy {Math.max(1, item.staff_required - item.staff_available)} additional staff or redirect walk-ins to digital kiosk.
          </span>
        </div>
      </div>

      {onTakeAction && (
        <button
          onClick={() => onTakeAction(item)}
          className="mt-3 w-full btn-secondary text-xs py-1.5 justify-between"
        >
          <span>Review AI Action Plan</span>
          <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
        </button>
      )}
    </div>
  );
};

export default BottleneckCard;
