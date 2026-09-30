import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import useWebSocket from "../hooks/useWebSocket";

const AlertContext = createContext(null);

export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([
    {
      id: "INIT-01",
      event: "BOTTLENECK_ALERT",
      branch_id: "BR001",
      service_category: "Loans - Payment and Sanctioning",
      risk_level: "HIGH",
      message: "Predicted wait exceeds 35 minutes due to high footfall surge.",
      timestamp: new Date().toLocaleTimeString(),
      read: false,
      data: { queue_length: 22, predicted_wait_minutes: 38.5, staff_available: 2 }
    },
    {
      id: "INIT-02",
      event: "STAFF_SHORTAGE",
      branch_id: "BR001",
      service_category: "KYC Related",
      risk_level: "MEDIUM",
      message: "KYC counter deficit of 1 staff member during peak 11:00-13:00.",
      timestamp: new Date().toLocaleTimeString(),
      read: false,
      data: { queue_length: 14, staff_available: 1, staff_required: 2 }
    }
  ]);

  const [toasts, setToasts] = useState([]);
  const [lastSurgeTimestamp, setLastSurgeTimestamp] = useState(null);

  const addToast = useCallback((toast) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 5);
    const newToast = { id, ...toast, createdAt: Date.now() };
    setToasts((prev) => [newToast, ...prev.slice(0, 4)]);

    // Auto dismiss after 6 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 6000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // Handle incoming real-time websocket message
  const handleWebSocketMessage = useCallback((msg) => {
    if (!msg || !msg.event || msg.event === "CONNECTED") return;

    const newAlert = {
      id: `WS-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      event: msg.event,
      branch_id: msg.branch_id || "BR001",
      service_category: msg.service_category || "General",
      risk_level: msg.risk_level || "HIGH",
      message: msg.message || "Real-time branch event received.",
      timestamp: msg.timestamp || new Date().toLocaleTimeString(),
      read: false,
      data: msg.data || {}
    };

    setAlerts((prev) => [newAlert, ...prev]);

    // Toast notification
    addToast({
      title: `${msg.event.replace(/_/g, " ")} (${newAlert.risk_level})`,
      message: newAlert.message,
      riskLevel: newAlert.risk_level,
      branch: newAlert.branch_id,
      service: newAlert.service_category
    });

    // Trigger dashboard reactive refresh without full page reload
    setLastSurgeTimestamp(Date.now());
  }, [addToast]);

  const { status: wsStatus, isConnected, reconnect } = useWebSocket(handleWebSocketMessage);

  const markAsRead = useCallback((alertId) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, read: true } : a))
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  const unreadCount = alerts.filter((a) => !a.read).length;

  const value = {
    alerts,
    unreadCount,
    toasts,
    wsStatus,
    isConnected,
    lastSurgeTimestamp,
    reconnect,
    addToast,
    removeToast,
    markAsRead,
    markAllAsRead,
    clearAlerts
  };

  return (
    <AlertContext.Provider value={value}>
      {children}
      {/* Real-time Global Toast Notifications Container */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none px-4 sm:px-0">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-2xl border backdrop-blur-xl transition-all duration-300 animate-slide-in ${
              toast.riskLevel === "CRITICAL"
                ? "bg-rose-950/90 border-rose-500/60 text-rose-100 shadow-rose-950/50"
                : toast.riskLevel === "HIGH"
                ? "bg-orange-950/90 border-orange-500/60 text-orange-100 shadow-orange-950/50"
                : "bg-slate-900/95 border-cyan-500/40 text-slate-100 shadow-cyan-950/50"
            }`}
          >
            <div className="mt-0.5 flex-shrink-0">
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                  {toast.title}
                </p>
                <span className="text-[10px] text-slate-400">{toast.branch}</span>
              </div>
              <p className="text-sm font-medium mt-0.5 leading-snug">{toast.message}</p>
              {toast.service && (
                <p className="text-xs text-slate-400 mt-1">Service: <span className="text-slate-300 font-semibold">{toast.service}</span></p>
              )}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-slate-400 hover:text-slate-200 text-xs px-1.5 py-1 rounded hover:bg-slate-800/50"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </AlertContext.Provider>
  );
};

export const useAlerts = () => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error("useAlerts must be used within an AlertProvider");
  }
  return context;
};

export default AlertContext;
