import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { BRANCHES } from "../utils/constants";

export function useBranch(initialBranchId = null) {
  const { user, role } = useAuth();
  
  const [selectedBranchId, setSelectedBranchId] = useState(() => {
    if (initialBranchId) return initialBranchId;
    if (user?.branch_id) return user.branch_id;
    return "BR001";
  });

  useEffect(() => {
    if (user?.branch_id && role !== "regional_ops") {
      setSelectedBranchId(user.branch_id);
    }
  }, [user, role]);

  const currentBranch = BRANCHES.find((b) => b.branch_id === selectedBranchId) || BRANCHES[0];

  return {
    selectedBranchId,
    setSelectedBranchId,
    currentBranch,
    allBranches: BRANCHES,
    isRegional: role === "regional_ops"
  };
}

export default useBranch;
