import React from "react";
import { useAlerts } from "../../context/AlertContext";
import RiskBadge from "../common/RiskBadge";
import { formatTime } from "../../utils/formatters";
import { Bell, Check, CheckCheck, Trash2, Radio } from "lucide-react";
import { Link } from "react-router-dom";

export const AlertPanel = ({ maxItems = 5, showViewAll = true }) => {
  const { alerts, unreadCount, markAsRead, markAllAsRead, wsStatus, isConnected } = useAlerts();

  const displayAlerts = alerts.slice(0, maxItems);

  return (
    <div className="glass-card p-5 border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Bell className="w-5 h-5 text-cyan-400" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center animate-pulse">
                {unreadCount}
              </span>
            )}
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-100">Live Operational Alerts</h3>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  isConnected ? "bg-emerald-400 animate-ping" : "bg-rose-500"
                }`}
              />
              <span className="text-[10px] text-slate-400 font-mono">
                {isConnected ? "WebSocket Connected" : `Gateway: ${wsStatus}`}
              </span>
            </div>
          </div>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <CheckCheck className="w-3.5 h-3.5" />
            Mark all read
          </button>
        )}
      </div>

      <div className="space-y-2.5">
        {displayAlerts.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No active operational alerts for this branch.
          </div>
        ) : (
          displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-3 rounded-xl border transition-all text-xs flex items-start justify-between gap-3 ${
                alert.read
                  ? "bg-slate-950/40 border-slate-800 text-slate-400"
                  : alert.risk_level === "CRITICAL"
                  ? "bg-rose-950/30 border-rose-500/50 text-slate-200"
                  : alert.risk_level === "HIGH"
                  ? "bg-orange-950/20 border-orange-500/40 text-slate-200"
                  : "bg-slate-900 border-slate-700 text-slate-200"
              }`}
            >
              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <RiskBadge risk={alert.risk_level} size="sm" />
                  <span className="font-mono text-[10px] text-slate-400">
                    {alert.branch_id}
                  </span>
                  <span className="text-[10px] text-slate-500">•</span>
                  <span className="text-[10px] text-slate-400">{formatTime(alert.timestamp)}</span>
                </div>
                <p className="font-semibold text-slate-100 text-xs leading-snug">
                  {alert.message}
                </p>
                {alert.service_category && (
                  <p className="text-[11px] text-slate-400">
                    Service: <span className="text-cyan-400 font-medium">{alert.service_category}</span>
                  </p>
                )}
              </div>

              {!alert.read && (
                <button
                  onClick={() => markAsRead(alert.id)}
                  title="Mark as Read"
                  className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-emerald-400 flex-shrink-0"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {showViewAll && alerts.length > maxItems && (
        <div className="mt-3 pt-2.5 border-t border-slate-800 text-center">
          <Link
            to="/alerts"
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors inline-flex items-center gap-1"
          >
            View all {alerts.length} audit alerts &rarr;
          </Link>
        </div>
      )}
    </div>
  );
};

export default AlertPanel;
