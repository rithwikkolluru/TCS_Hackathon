import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { DEMO_CREDENTIALS } from "../utils/constants";
import { ShieldCheck, Lock, Mail, ArrowRight, AlertCircle, Sparkles, Building2, UserCheck, Globe2 } from "lucide-react";

export const Login = () => {
  const { login, loading, authError, setAuthError } = useAuth();
  const [email, setEmail] = useState("manager_hyd@bank.com");
  const [password, setPassword] = useState("BankDemo#2026");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setAuthError("Please provide both email and password.");
      return;
    }
    await login(email, password);
  };

  const handleDemoSelect = (cred) => {
    setEmail(cred.email);
    setPassword(cred.password);
    setAuthError(null);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center p-4 sm:p-6 bg-slate-950 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-md w-full glass-card p-6 sm:p-8 border-slate-800 bg-slate-900/90 shadow-2xl relative z-10">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-xl shadow-cyan-500/20 mb-3">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white">
            Intelligent Branch AI
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Service Load & Customer Experience Optimizer
          </p>
        </div>

        {/* Error Alert */}
        {authError && (
          <div className="mb-4 p-3 bg-rose-950/50 border border-rose-500/40 rounded-xl text-xs text-rose-300 flex items-start gap-2.5 animate-shake">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <span>{authError}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Staff Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@bank.com"
                required
                className="input-field pl-9 text-xs"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Secure Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="input-field pl-9 text-xs"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-2.5 text-xs font-bold mt-2"
          >
            {loading ? "Authenticating Credentials..." : "Sign In to Branch Portal"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Demo Logins Section */}
        <div className="mt-6 pt-5 border-t border-slate-800">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Quick Demo Login Roles
            </span>
          </div>
          <div className="space-y-2">
            {DEMO_CREDENTIALS.map((cred) => {
              const isSelected = email === cred.email;
              const Icon = cred.role === "regional_ops" ? Globe2 : cred.role === "manager" ? Building2 : UserCheck;

              return (
                <button
                  key={cred.role}
                  type="button"
                  onClick={() => handleDemoSelect(cred)}
                  className={`w-full text-left p-2.5 rounded-lg border text-xs transition-all flex items-center justify-between gap-2 ${
                    isSelected
                      ? "bg-cyan-950/30 border-cyan-500/50 text-cyan-200"
                      : "bg-slate-950/50 border-slate-800/80 hover:bg-slate-800 text-slate-300"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Icon className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                    <div className="truncate">
                      <p className="font-bold truncate">{cred.label}</p>
                      <p className="text-[10px] text-slate-400 truncate">{cred.email}</p>
                    </div>
                  </div>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    {cred.role.replace(/_/g, " ")}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
