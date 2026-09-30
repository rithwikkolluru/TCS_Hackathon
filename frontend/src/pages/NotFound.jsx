import React from "react";
import { Link } from "react-router-dom";
import { FileQuestion, ArrowLeft } from "lucide-react";

export const NotFound = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-6 text-center">
      <div className="glass-card max-w-md w-full p-8 border-slate-800">
        <div className="w-16 h-16 rounded-2xl bg-slate-850 border border-slate-700 flex items-center justify-center mx-auto mb-4 text-cyan-400">
          <FileQuestion className="w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-white">404 - Page Not Found</h1>
        <p className="text-xs text-slate-400 mt-2">
          The banking resource or route you requested does not exist or has been relocated.
        </p>
        <div className="mt-6">
          <Link to="/" className="btn-primary text-xs">
            <ArrowLeft className="w-4 h-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
