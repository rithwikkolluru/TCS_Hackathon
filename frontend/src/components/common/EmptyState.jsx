import React from "react";
import { FolderOpen } from "lucide-react";

export const EmptyState = ({
  icon: Icon = FolderOpen,
  title = "No data available",
  message = "No records found matching your current filter criteria.",
  action = null
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center glass-card my-4">
      <div className="p-3.5 bg-slate-800/60 rounded-2xl text-slate-400 mb-3 border border-slate-700/50">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-base font-semibold text-slate-200 mb-1">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mb-4">{message}</p>
      {action}
    </div>
  );
};

export default EmptyState;
