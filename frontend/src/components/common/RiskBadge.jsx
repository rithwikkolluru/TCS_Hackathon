import React from "react";
import { RISK_LEVELS } from "../../utils/constants";

export const RiskBadge = ({ risk, size = "md", className = "" }) => {
  const normRisk = String(risk || "LOW").toUpperCase();
  const config = RISK_LEVELS[normRisk] || RISK_LEVELS.LOW;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-0.5 text-xs",
    lg: "px-3 py-1 text-sm font-bold"
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full uppercase tracking-wider ${config.badgeClass} ${sizeClasses[size] || sizeClasses.md} ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          normRisk === "CRITICAL"
            ? "bg-rose-400 animate-ping"
            : normRisk === "HIGH"
            ? "bg-orange-400"
            : normRisk === "MEDIUM"
            ? "bg-amber-400"
            : "bg-emerald-400"
        }`}
      />
      {config.label}
    </span>
  );
};

export default RiskBadge;
