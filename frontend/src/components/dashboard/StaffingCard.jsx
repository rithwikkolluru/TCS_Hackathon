import React from "react";
import { Users, Clock, AlertTriangle, CheckCircle2 } from "lucide-react";
import StatusBadge from "../common/StatusBadge";

export const StaffingCard = ({ item }) => {
  if (!item) return null;

  const shortage = item.additional_staff_required || item.staff_gap || 0;
  const isShortage = shortage > 0;

  return (
    <div className={`glass-card p-4 border-slate-800 ${isShortage ? "border-amber-500/30 bg-amber-950/10" : ""}`}>
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-sm text-slate-100 font-mono">
            {item.time_window || item.time_slot || "11:00 - 13:00"}
          </span>
        </div>
        <StatusBadge status={isShortage ? "SHORTAGE" : "OPTIMAL"} />
      </div>

      <div className="grid grid-cols-3 gap-2 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 mb-3 text-center">
        <div>
          <span className="text-[10px] text-slate-400 uppercase block font-medium">Exp. Volume</span>
          <span className="font-mono font-bold text-sm text-slate-100">
            {item.predicted_customers || item.expected_customers || 120}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase block font-medium">Available</span>
          <span className="font-mono font-bold text-sm text-emerald-400">
            {item.staff_available || 4}
          </span>
        </div>
        <div>
          <span className="text-[10px] text-slate-400 uppercase block font-medium">Required</span>
          <span className="font-mono font-bold text-sm text-cyan-400">
            {item.staff_required || 6}
          </span>
        </div>
      </div>

      {isShortage ? (
        <div className="flex items-start gap-2 text-xs bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg text-rose-300">
          <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Staffing Gap: +{shortage} Employee(s) Needed</span>
            <p className="text-[11px] text-rose-200/80 mt-0.5">
              {item.explanation || "Projected volume will induce counter queuing beyond acceptable waiting threshold."}
            </p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-xs bg-emerald-500/10 border border-emerald-500/20 p-2.5 rounded-lg text-emerald-300">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span className="font-medium">Capacity optimal. Staff allocations cover forecasted arrival variance.</span>
        </div>
      )}
    </div>
  );
};

export default StaffingCard;
