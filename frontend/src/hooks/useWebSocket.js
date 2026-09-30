import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "../context/AuthContext";

const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export function useWebSocket(onMessageReceived) {
  const { token, isAuthenticated } = useAuth();
  const [status, setStatus] = useState("disconnected"); // 'connected' | 'connecting' | 'disconnected' | 'error'
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!token || !isAuthenticated()) {
      setStatus("disconnected");
      return;
    }

    // Clean previous socket
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (e) {}
    }

    const wsUrl = `${WS_BASE_URL}/ws/alerts?token=${encodeURIComponent(token)}`;
    setStatus("connecting");

    try {
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        if (!mountedRef.current) return;
        setStatus("connected");
        console.log("[WebSocket] Real-time channel established.");

        // Keep-alive ping every 25 seconds
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send("ping");
          }
        }, 25000);
      };

      socket.onmessage = (event) => {
        if (!mountedRef.current) return;
        try {
          if (event.data === "pong") return;
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessageReceived) {
            onMessageReceived(data);
          }
        } catch (err) {
          console.warn("[WebSocket] Error parsing message:", err);
        }
      };

      socket.onerror = (err) => {
        console.warn("[WebSocket] Connection error:", err);
        if (mountedRef.current) {
          setStatus("error");
        }
      };

      socket.onclose = (event) => {
        if (!mountedRef.current) return;
        setStatus("disconnected");
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);

        // Auto-reconnect after 3 seconds unless normal closure or unmounted
        if (event.code !== 1000 && event.code !== 4001) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              console.log("[WebSocket] Attempting auto-reconnect...");
              connect();
            }
          }, 3000);
        }
      };
    } catch (e) {
      console.error("[WebSocket] Exception creating WebSocket:", e);
      setStatus("error");
    }
  }, [token, isAuthenticated, onMessageReceived]);

  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
      if (wsRef.current) {
        try {
          wsRef.current.close(1000, "Component unmounted");
        } catch (e) {}
      }
    };
  }, [connect]);

  const sendMessage = useCallback((msg) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof msg === "string" ? msg : JSON.stringify(msg));
      return true;
    }
    return false;
  }, []);

  return {
    status,
    lastMessage,
    sendMessage,
    reconnect: connect,
    isConnected: status === "connected"
  };
}

export default useWebSocket;
