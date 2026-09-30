import React from "react";
import { Smartphone, Zap, Clock, CheckCircle } from "lucide-react";

export const DigitalOpportunityCard = ({ item }) => {
  if (!item) return null;

  return (
    <div className="glass-card p-4 border-slate-800 hover:border-cyan-500/40 transition-all">
      <div className="flex items-start justify-between gap-3 mb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Smartphone className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-slate-100">{item.service_category}</h4>
            <span className="text-[11px] text-cyan-400 font-semibold flex items-center gap-1 mt-0.5">
              <Zap className="w-3 h-3" />
              Channel: {item.digital_channel || "Mobile App & NetBanking"}
            </span>
          </div>
        </div>
        <span className="bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded text-[11px] font-bold">
          {Math.round((item.confidence || 0.85) * 100)}% Match
        </span>
      </div>

      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 my-2.5 flex items-center justify-between text-xs">
        <span className="text-slate-400">Est. Branch Time Saved:</span>
        <span className="font-mono font-bold text-emerald-400 flex items-center gap-1">
          <Clock className="w-3.5 h-3.5" />
          ~{item.estimated_branch_time_saved_minutes || 5.0} mins/customer
        </span>
      </div>

      <div className="space-y-1.5 text-xs text-slate-300 border-t border-slate-800/80 pt-2.5">
        <p className="text-slate-400 leading-relaxed">
          {item.recommendation || item.explanation || item.instructions || "Encourage self-service onboarding for standard transactions."}
        </p>
      </div>
    </div>
  );
};

export default DigitalOpportunityCard;
