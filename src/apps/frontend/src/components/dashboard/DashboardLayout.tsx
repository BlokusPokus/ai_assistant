import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';
import { useDashboardStore } from '@/stores/dashboardStore';

const DashboardLayout: React.FC = () => {
  const { isSidebarCollapsed, toggleSidebar } = useDashboardStore();

  const contentMargin = isSidebarCollapsed ? 'ml-16' : 'ml-64';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />

      {/* Main content area */}
      <div
        className={`transition-all duration-300 ease-in-out ${contentMargin}`}
      >
        {/* Header */}
        <DashboardHeader onMenuToggle={toggleSidebar} />

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
