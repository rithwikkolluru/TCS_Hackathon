import React from "react";

export const StatusBadge = ({ status }) => {
  const norm = String(status || "PENDING").toUpperCase();

  const styles = {
    PENDING: "bg-amber-500/10 text-amber-300 border-amber-500/30",
    ACCEPTED: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
    REJECTED: "bg-rose-500/10 text-rose-300 border-rose-500/30",
    MODIFIED: "bg-blue-500/10 text-blue-300 border-blue-500/30",
    EXPIRED: "bg-slate-500/10 text-slate-400 border-slate-600/30",
    AVAILABLE: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    SHORTAGE: "bg-rose-500/10 text-rose-400 border-rose-500/30",
    OPTIMAL: "bg-cyan-500/10 text-cyan-400 border-cyan-500/30",
    OPERATIONAL: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
  };

  const styleClass = styles[norm] || "bg-slate-800 text-slate-300 border-slate-700";

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold uppercase tracking-wider border ${styleClass}`}
    >
      {norm}
    </span>
  );
};

export default StatusBadge;
