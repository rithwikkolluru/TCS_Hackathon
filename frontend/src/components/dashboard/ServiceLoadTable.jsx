import React from "react";
import RiskBadge from "../common/RiskBadge";
import { formatMinutes } from "../../utils/formatters";

export const ServiceLoadTable = ({ items = [], onSelectService = null }) => {
  if (!items || items.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 text-sm">
        No service load data available for this branch.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto w-full">
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-semibold">
          <tr>
            <th className="py-3 px-4">Service Category</th>
            <th className="py-3 px-3 text-center">Current Queue</th>
            <th className="py-3 px-3 text-center">Predicted Wait</th>
            <th className="py-3 px-3 text-center">Staff Available</th>
            <th className="py-3 px-3 text-center">Staff Required</th>
            <th className="py-3 px-3 text-center">Operational Risk</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {items.map((item, idx) => {
            const isDeficit = item.staff_required > item.staff_available;
            const isHighRisk = item.risk_level === "HIGH" || item.risk_level === "CRITICAL";

            return (
              <tr
                key={idx}
                onClick={() => onSelectService && onSelectService(item)}
                className={`transition-colors ${
                  isHighRisk
                    ? "bg-rose-950/10 hover:bg-rose-950/20"
                    : "hover:bg-slate-800/40"
                } ${onSelectService ? "cursor-pointer" : ""}`}
              >
                <td className="py-3 px-4 font-semibold text-slate-200">
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        item.risk_level === "CRITICAL"
                          ? "bg-rose-500 animate-ping"
                          : item.risk_level === "HIGH"
                          ? "bg-orange-500"
                          : item.risk_level === "MEDIUM"
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                    />
                    <span className="line-clamp-1">{item.service_category}</span>
                  </div>
                </td>
                <td className="py-3 px-3 text-center font-mono font-bold text-slate-100">
                  {item.queue_length}
                </td>
                <td className="py-3 px-3 text-center font-mono font-bold text-cyan-400">
                  {formatMinutes(item.predicted_wait || item.average_wait)}
                </td>
                <td className="py-3 px-3 text-center font-mono text-emerald-400">
                  {item.staff_available}
                </td>
                <td className="py-3 px-3 text-center font-mono">
                  <span
                    className={
                      isDeficit
                        ? "text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/30"
                        : "text-slate-300"
                    }
                  >
                    {item.staff_required}
                  </span>
                </td>
                <td className="py-3 px-3 text-center">
                  <RiskBadge risk={item.risk_level} size="sm" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ServiceLoadTable;
