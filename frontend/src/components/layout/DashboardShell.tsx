/**
 * ConstructMind AI - Dashboard Page Layout Shell
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import { CommandPalette } from './CommandPalette';
import { CopilotButton } from '../copilot/CopilotButton';
import { CopilotPanel } from '../copilot/CopilotPanel';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';

interface DashboardShellProps {
  children: React.ReactNode;
}

export function DashboardShell({ children }: DashboardShellProps) {
  const { sidebarCollapsed } = useUIStore();
  const { fetchProjects } = useProjectStore();

  // Load projects on shell load
  React.useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <div className="min-h-screen bg-background text-foreground flex overflow-hidden">
      {/* Sidebar Layout */}
      <Sidebar />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
        {/* Top Navbar */}
        <Navbar />

        {/* Dynamic Page Container */}
        <motion.main
          animate={{ paddingLeft: sidebarCollapsed ? 72 : 260 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          className="flex-1 overflow-y-auto w-full transition-all duration-300"
        >
          <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-8">
            {children}
          </div>
        </motion.main>
      </div>

      {/* Global Overlays */}
      <CommandPalette />
      
      {/* AI Copilot Panel and Floating Trigger */}
      <CopilotButton />
      <CopilotPanel />
    </div>
  );
}
export default DashboardShell;
