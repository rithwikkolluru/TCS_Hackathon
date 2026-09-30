import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export const ErrorState = ({
  title = "Unable to load data",
  message = "An error occurred while fetching information from the banking backend server.",
  onRetry = null,
  code = null
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center glass-card border-rose-900/30 bg-rose-950/10 my-4">
      <div className="p-3 bg-rose-500/10 rounded-full text-rose-400 mb-3 border border-rose-500/20">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h3 className="text-base font-bold text-slate-100 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-md mb-4">{message}</p>
      {code && (
        <span className="text-[11px] font-mono bg-slate-900 text-slate-400 px-2.5 py-1 rounded border border-slate-800 mb-4">
          Status Code: {code}
        </span>
      )}
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-xs">
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
};

export default ErrorState;
