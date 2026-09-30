import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useAlerts } from "../context/AlertContext";
import { BranchSelector } from "../components/common/BranchSelector";
import { SurgeTriggerModal } from "../components/dashboard/SurgeTriggerModal";
import {
  Menu,
  Bell,
  Zap,
  Building2,
  Shield,
  LogOut,
  ChevronDown,
  Sparkles,
  Radio
} from "lucide-react";

export const Topbar = ({ onOpenMobileSidebar, selectedBranch, onSelectBranch }) => {
  const { user, role, logout } = useAuth();
  const { unreadCount, isConnected } = useAlerts();
  const [isSurgeModalOpen, setIsSurgeModalOpen] = useState(false);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <>
      <header className="sticky top-0 z-30 h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 flex items-center justify-between gap-4">
        {/* Left Section: Mobile Menu Trigger + Branch Selector */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenMobileSidebar}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 lg:hidden"
            aria-label="Open sidebar navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Branch Selector if applicable */}
          <div className="hidden sm:block">
            <BranchSelector
              selectedBranch={selectedBranch}
              onSelectBranch={onSelectBranch}
              showAllOption={role === "regional_ops"}
            />
          </div>
        </div>

        {/* Right Section: Surge Demo Trigger + Alerts Bell + Profile */}
        <div className="flex items-center gap-3">
          {/* Live Surge Simulation Trigger Button (Demo Highlight) */}
          <button
            onClick={() => setIsSurgeModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-rose-600/20 to-orange-600/20 hover:from-rose-600/30 hover:to-orange-600/30 border border-rose-500/40 text-rose-300 rounded-lg text-xs font-bold transition-all shadow-sm group"
            title="Simulate Instantaneous Customer Surge"
          >
            <Zap className="w-3.5 h-3.5 text-rose-400 group-hover:scale-110 transition-transform" />
            <span className="hidden md:inline">Simulate Live Surge</span>
          </button>

          {/* WebSocket Status Indicator */}
          <div
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-[11px]"
            title={`WebSocket Gateway Status: ${isConnected ? "Connected" : "Disconnected"}`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? "bg-emerald-400 animate-pulse" : "bg-rose-500"
              }`}
            />
            <span className="font-mono text-slate-300">
              {isConnected ? "WS Live" : "WS Offline"}
            </span>
          </div>

          {/* Notifications Bell */}
          <Link
            to="/alerts"
            className="relative p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
            title="View Real-Time Alerts"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center animate-pulse">
                {unreadCount}
              </span>
            )}
          </Link>

          {/* User Profile dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
              className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-800/80 text-slate-200 text-xs font-semibold transition-colors"
            >
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white font-bold text-xs uppercase">
                {user?.name ? user.name[0] : "U"}
              </div>
              <span className="hidden md:inline max-w-[120px] truncate">{user?.name}</span>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </button>

            {isProfileMenuOpen && (
              <>
                <div
                  onClick={() => setIsProfileMenuOpen(false)}
                  className="fixed inset-0 z-20"
                />
                <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl py-1.5 z-30 animate-fade-in text-xs">
                  <div className="px-3 py-2 border-b border-slate-800">
                    <p className="font-bold text-slate-200 truncate">{user?.name}</p>
                    <p className="text-[10px] text-slate-400 font-mono capitalize">{role}</p>
                  </div>
                  <Link
                    to="/profile"
                    onClick={() => setIsProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    <Shield className="w-3.5 h-3.5 text-cyan-400" />
                    Security & Profile
                  </Link>
                  <button
                    onClick={() => {
                      setIsProfileMenuOpen(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-rose-400 hover:bg-rose-500/10 text-left font-semibold"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Sign Out
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Live Surge Simulation Modal */}
      <SurgeTriggerModal
        isOpen={isSurgeModalOpen}
        onClose={() => setIsSurgeModalOpen(false)}
        branchId={selectedBranch || "BR001"}
      />
    </>
  );
};

export default Topbar;
