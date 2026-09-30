import React from "react";
import { Building2 } from "lucide-react";
import { BRANCHES } from "../../utils/constants";
import { useAuth } from "../../context/AuthContext";

export const BranchSelector = ({
  selectedBranch,
  onSelectBranch,
  showAllOption = false,
  className = ""
}) => {
  const { role } = useAuth();
  const isRegional = role === "regional_ops";

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Building2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
      <select
        value={selectedBranch || "BR001"}
        onChange={(e) => onSelectBranch(e.target.value)}
        disabled={!isRegional} // Non-regional users are locked to their branch
        className="select-field text-xs py-1.5 px-3 bg-slate-900 border-slate-700 text-slate-200 cursor-pointer font-medium disabled:opacity-80 disabled:cursor-not-allowed"
      >
        {showAllOption && isRegional && (
          <option value="NETWORK_ALL">All Network Branches (Aggregated)</option>
        )}
        {BRANCHES.map((b) => (
          <option key={b.branch_id} value={b.branch_id}>
            {b.branch_name} ({b.branch_id}) - {b.city}
          </option>
        ))}
      </select>
    </div>
  );
};

export default BranchSelector;
