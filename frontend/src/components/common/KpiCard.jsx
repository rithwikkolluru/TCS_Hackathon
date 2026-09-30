import React from "react";
import RiskBadge from "./RiskBadge";

export const KpiCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive = true,
  risk = null,
  accent = "cyan",
  onClick = null,
  highlight = false,
  className = ""
}) => {
  const accentColors = {
    cyan: "from-cyan-500/20 to-blue-500/5 text-cyan-400 border-cyan-500/30",
    emerald: "from-emerald-500/20 to-teal-500/5 text-emerald-400 border-emerald-500/30",
    amber: "from-amber-500/20 to-orange-500/5 text-amber-400 border-amber-500/30",
    rose: "from-rose-500/20 to-red-500/5 text-rose-400 border-rose-500/30",
    indigo: "from-indigo-500/20 to-purple-500/5 text-indigo-400 border-indigo-500/30"
  };

  const accentStyle = accentColors[accent] || accentColors.cyan;

  return (
    <div
      onClick={onClick}
      className={`glass-card p-5 relative overflow-hidden transition-all duration-300 ${
        highlight ? "ring-2 ring-cyan-500/50 bg-slate-900/90" : "hover:border-slate-700"
      } ${onClick ? "cursor-pointer hover:scale-[1.01]" : ""} ${className}`}
    >
      {/* Background glow accent */}
      <div
        className={`absolute -right-6 -top-6 w-24 h-24 bg-gradient-to-br ${accentStyle} rounded-full blur-2xl opacity-40 pointer-events-none`}
      />

      <div className="flex items-center justify-between gap-3 mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 line-clamp-1">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 ${accentStyle.split(" ")[2]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between gap-2 mt-1">
        <div className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight font-mono">
          {value}
        </div>
        {risk && <RiskBadge risk={risk} size="sm" />}
      </div>

      {(subtitle || trend) && (
        <div className="flex items-center justify-between text-xs mt-3 pt-2.5 border-t border-slate-800/80 text-slate-400">
          <span className="truncate">{subtitle}</span>
          {trend && (
            <span
              className={`font-semibold ml-2 flex-shrink-0 ${
                trendPositive ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {trend}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default KpiCard;
