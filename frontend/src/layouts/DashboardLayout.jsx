import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import useBranch from "../hooks/useBranch";

export const DashboardLayout = () => {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { selectedBranchId, setSelectedBranchId, currentBranch } = useBranch();

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <Sidebar
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        {/* Topbar */}
        <Topbar
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          selectedBranch={selectedBranchId}
          onSelectBranch={setSelectedBranchId}
        />

        {/* Dynamic Nested Content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto animate-fade-in">
          <Outlet context={{ selectedBranchId, setSelectedBranchId, currentBranch }} />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
