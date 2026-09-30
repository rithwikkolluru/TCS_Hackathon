import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useAlerts } from "../context/AlertContext";
import {
  LayoutDashboard,
  BarChart3,
  Users,
  AlertTriangle,
  Lightbulb,
  MessageSquare,
  Bell,
  Building2,
  CheckSquare,
  UserCheck,
  LogOut,
  Radio,
  Shield,
  Layers,
  ChevronRight
} from "lucide-react";

export const Sidebar = ({ isMobileOpen, onCloseMobile }) => {
  const { user, role, logout } = useAuth();
  const { unreadCount, isConnected } = useAlerts();

  // Permitted navigation items based on authoritative RBAC
  const getNavLinks = () => {
    if (role === "manager") {
      return [
        { label: "Dashboard", to: "/manager", icon: LayoutDashboard },
        { label: "Service Load", to: "/service-load", icon: BarChart3 },
        { label: "Staffing", to: "/staffing", icon: Users },
        { label: "Bottlenecks", to: "/bottlenecks", icon: AlertTriangle },
        { label: "Recommendations", to: "/recommendations", icon: Lightbulb },
        { label: "Feedback & CX", to: "/feedback", icon: MessageSquare },
        { label: "Live Alerts", to: "/alerts", icon: Bell, badge: unreadCount },
        { label: "My Profile", to: "/profile", icon: Shield }
      ];
    }

    if (role === "employee") {
      return [
        { label: "Dashboard", to: "/employee", icon: LayoutDashboard },
        { label: "My Tasks", to: "/employee/tasks", icon: CheckSquare },
        { label: "Service Load", to: "/service-load", icon: BarChart3 },
        { label: "Live Alerts", to: "/alerts", icon: Bell, badge: unreadCount },
        { label: "My Profile", to: "/profile", icon: Shield }
      ];
    }

    if (role === "regional_ops") {
      return [
        { label: "Regional Dashboard", to: "/regional", icon: LayoutDashboard },
        { label: "Branches Network", to: "/branches", icon: Building2 },
        { label: "Network Load", to: "/service-load", icon: BarChart3 },
        { label: "Bottlenecks", to: "/bottlenecks", icon: AlertTriangle },
        { label: "Staffing Allocations", to: "/staffing", icon: Users },
        { label: "Feedback & CX", to: "/feedback", icon: MessageSquare },
        { label: "Network Alerts", to: "/alerts", icon: Bell, badge: unreadCount },
        { label: "Regional Profile", to: "/profile", icon: Shield }
      ];
    }

    // Default fallback
    return [
      { label: "Dashboard", to: "/", icon: LayoutDashboard },
      { label: "Live Alerts", to: "/alerts", icon: Bell, badge: unreadCount },
      { label: "My Profile", to: "/profile", icon: Shield }
    ];
  };

  const navLinks = getNavLinks();

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-64 bg-slate-900/95 border-r border-slate-800/80 backdrop-blur-xl flex flex-col justify-between transition-transform duration-300 lg:translate-x-0 ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="p-5 border-b border-slate-800 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white font-black text-lg">
              B
            </div>
            <div>
              <h2 className="font-bold text-sm tracking-tight text-white leading-none">
                BANKING AI
              </h2>
              <p className="text-[10px] text-cyan-400 font-semibold tracking-wider uppercase mt-1">
                Load & CX Optimizer
              </p>
            </div>
          </div>

          {/* User Badge Overview */}
          <div className="p-3 mx-3 my-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-cyan-400 font-bold text-xs uppercase border border-slate-700">
              {user?.name ? user.name[0] : "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-slate-200 truncate">{user?.name || "Staff Member"}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] font-mono text-cyan-400 capitalize font-medium">
                  {role?.replace(/_/g, " ") || "Staff"}
                </span>
                {user?.branch_id && (
                  <span className="text-[9px] bg-slate-800 text-slate-400 px-1 rounded font-mono">
                    {user.branch_id}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="px-3 space-y-1 mt-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                    }`
                  }
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </div>
                  {link.badge !== undefined && link.badge > 0 && (
                    <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-rose-500 text-white animate-pulse">
                      {link.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Footer & Gateway Status */}
        <div className="p-3 border-t border-slate-800 space-y-2">
          <div className="flex items-center justify-between px-3 py-2 bg-slate-950/60 rounded-lg text-[10px] border border-slate-800">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Radio className="w-3 h-3 text-cyan-400" />
              Live WS Stream:
            </span>
            <span
              className={`font-semibold font-mono ${
                isConnected ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {isConnected ? "ONLINE" : "OFFLINE"}
            </span>
          </div>

          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out Session</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
