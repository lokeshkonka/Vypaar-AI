import React, { useState } from "react";
import { ErrorBoundary } from "../common/ErrorBoundary";
import Navbar from "../dashboard/Navbar/Navbar";
import UserSync from "../dashboard/Navbar/UserSync";
import Sidebar from "../dashboard/Sidebar";
import GraphBackgroundCorner from "../Background/GraphBackgroundCorner";

interface DashboardLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

/**
 * DashboardLayout - Main layout wrapper for authenticated dashboard pages
 * Provides consistent structure: Navbar, Sidebar, ErrorBoundary, and content
 */
export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  showSidebar = true,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ErrorBoundary>
      <div className="dashboard relative min-h-screen overflow-hidden">
        <GraphBackgroundCorner />
        <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <UserSync />

        {showSidebar && (
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        )}

        {/* Main content */}
        <main className="dashboard-body relative z-10">
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </ErrorBoundary>
  );
};

export default DashboardLayout;
