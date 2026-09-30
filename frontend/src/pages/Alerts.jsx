import React, { useState } from "react";
import { useAlerts } from "../context/AlertContext";
import RiskBadge from "../components/common/RiskBadge";
import { formatTime } from "../utils/formatters";
import {
  Bell,
  Check,
  CheckCheck,
  Radio,
  RefreshCw,
  Filter,
  Info,
  X,
  AlertTriangle
} from "lucide-react";

export const Alerts = () => {
  const {
    alerts,
    unreadCount,
    markAsRead,
    markAllAsRead,
    wsStatus,
    isConnected,
    reconnect
  } = useAlerts();

  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterRisk, setFilterRisk] = useState("ALL");
  const [filterRead, setFilterRead] = useState("ALL");

  const filteredAlerts = alerts.filter((a) => {
    if (filterRisk !== "ALL" && a.risk_level !== filterRisk) return false;
    if (filterRead === "UNREAD" && a.read) return false;
    if (filterRead === "READ" && !a.read) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-5 border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  isConnected ? "bg-emerald-400 animate-ping" : "bg-rose-500"
                }`}
              />
              <span className="text-xs font-mono text-cyan-400 font-bold">
                WEBSOCKET STATUS: {isConnected ? "STREAM ACTIVE" : wsStatus.toUpperCase()}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white mt-1 flex items-center gap-2">
              <Bell className="w-5 h-5 text-cyan-400" />
              Real-Time Operational Alerts & Event Stream
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Live broadcast telemetry for queue spikes, bottleneck thresholds, staff shortages, and surge events
            </p>
          </div>

          <div className="flex items-center gap-2">
            {!isConnected && (
              <button onClick={reconnect} className="btn-secondary text-xs">
                <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
                <span>Reconnect WebSocket</span>
              </button>
            )}
            {unreadCount > 0 && (
              <button onClick={markAllAsRead} className="btn-primary text-xs">
                <CheckCheck className="w-3.5 h-3.5" />
                <span>Mark All ({unreadCount}) Read</span>
              </button>
            )}
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 mt-4 border-t border-slate-800">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1">
              <Filter className="w-3.5 h-3.5" />
              Risk Level:
            </span>
            {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((risk) => (
              <button
                key={risk}
                onClick={() => setFilterRisk(risk)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  filterRisk === risk
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                    : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                {risk}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">Read State:</span>
            <select
              value={filterRead}
              onChange={(e) => setFilterRead(e.target.value)}
              className="select-field text-xs py-1 px-2.5"
            >
              <option value="ALL">All Alerts</option>
              <option value="UNREAD">Unread Only</option>
              <option value="READ">Read Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Alerts Table (Requirement 11: Time | Branch | Service | Risk | Message | Status) */}
      <div className="glass-card p-5 border-slate-800">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-semibold">
              <tr>
                <th className="py-3 px-4">Time</th>
                <th className="py-3 px-3">Branch</th>
                <th className="py-3 px-3">Service</th>
                <th className="py-3 px-3 text-center">Risk Tier</th>
                <th className="py-3 px-4">Operational Message</th>
                <th className="py-3 px-3 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                    No alerts match your filter criteria.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alert) => {
                  const isCrit = alert.risk_level === "CRITICAL";

                  return (
                    <tr
                      key={alert.id}
                      className={`transition-colors ${
                        !alert.read
                          ? isCrit
                            ? "bg-rose-950/20 hover:bg-rose-950/30"
                            : "bg-slate-900/80 hover:bg-slate-850"
                          : "hover:bg-slate-800/30 opacity-75"
                      }`}
                    >
                      <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                        {formatTime(alert.timestamp)}
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-cyan-400 whitespace-nowrap">
                        {alert.branch_id}
                      </td>
                      <td className="py-3 px-3 text-slate-200 font-medium">
                        {alert.service_category || "General"}
                      </td>
                      <td className="py-3 px-3 text-center">
                        <RiskBadge risk={alert.risk_level} size="sm" />
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-100 max-w-md">
                        {alert.message}
                      </td>
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            alert.read
                              ? "bg-slate-800 text-slate-400 border border-slate-700"
                              : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                          }`}
                        >
                          {alert.read ? "READ" : "UNREAD"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right space-x-2 whitespace-nowrap">
                        <button
                          onClick={() => {
                            setSelectedAlert(alert);
                            if (!alert.read) markAsRead(alert.id);
                          }}
                          className="btn-secondary text-[11px] py-1 px-2.5"
                        >
                          <Info className="w-3 h-3 text-cyan-400" />
                          <span>Details</span>
                        </button>
                        {!alert.read && (
                          <button
                            onClick={() => markAsRead(alert.id)}
                            className="btn-success text-[11px] py-1 px-2"
                            title="Mark as Read"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
          <div className="glass-card max-w-lg w-full p-6 border-slate-700 bg-slate-900 shadow-2xl relative">
            <button
              onClick={() => setSelectedAlert(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Bell className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">
                  {selectedAlert.event?.replace(/_/g, " ")}
                </h3>
                <p className="text-xs text-slate-400">
                  Branch {selectedAlert.branch_id} • {formatTime(selectedAlert.timestamp)}
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs bg-slate-950/60 p-4 rounded-xl border border-slate-800 mb-5">
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Operational Risk:</span>
                <RiskBadge risk={selectedAlert.risk_level} size="sm" />
              </div>
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-400">Service Category:</span>
                <span className="font-semibold text-slate-200">{selectedAlert.service_category}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1 font-semibold">Message Payload:</span>
                <p className="text-slate-200 leading-relaxed bg-slate-900 p-2.5 rounded border border-slate-800">
                  {selectedAlert.message}
                </p>
              </div>

              {selectedAlert.data && Object.keys(selectedAlert.data).length > 0 && (
                <div>
                  <span className="text-slate-400 block mb-1 font-semibold">Telemetry Data:</span>
                  <pre className="text-[11px] font-mono text-cyan-300 bg-slate-900 p-2.5 rounded border border-slate-800 overflow-x-auto">
                    {JSON.stringify(selectedAlert.data, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setSelectedAlert(null)}
                className="btn-primary text-xs"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;
