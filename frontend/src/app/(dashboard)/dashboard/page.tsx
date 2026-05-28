/**
 * ConstructMind AI - Executive Controls Dashboard
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { 
  Sparkles, 
  TrendingUp, 
  TrendingDown, 
  AlertOctagon, 
  Clock, 
  DollarSign, 
  FolderGit2,
  CalendarDays
} from 'lucide-react';
import { useProjectStore } from '@/store/project-store';
import { useScheduleStore } from '@/store/schedule-store';
import { KPICard } from '@/components/dashboard/KPICard';
import { ProjectHealthScore } from '@/components/dashboard/ProjectHealthScore';
import { AIInsightCard } from '@/components/dashboard/AIInsightCard';
import { SCurveChart } from '@/components/dashboard/SCurveChart';
import { ResourceHistogram } from '@/components/dashboard/ResourceHistogram';
import { CriticalActivitiesTable } from '@/components/dashboard/CriticalActivitiesTable';
import { ActivityTimeline } from '@/components/dashboard/ActivityTimeline';
import { Badge } from '@/components/shared/Badge';
import { cn } from '@/lib/utils';

export default function DashboardPage() {
  const { projects, activeProject, selectProject } = useProjectStore();
  const { fetchGanttData, fetchActivities, fetchResources, fetchAssignments, fetchBOQItems } = useScheduleStore();

  // Load project-related data on active project select
  React.useEffect(() => {
    if (activeProject) {
      fetchGanttData(activeProject.id);
      fetchActivities(activeProject.id);
      fetchResources(activeProject.id);
      fetchAssignments(activeProject.id);
      fetchBOQItems(activeProject.id);
    }
  }, [activeProject, fetchGanttData, fetchActivities, fetchResources, fetchAssignments, fetchBOQItems]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 100 } }
  };

  const aiInsightsList = [
    "Schedule Performance Index (SPI) is 0.91. We recommend fast-tracking internal wall plastering by converting its dependency from FS to SS with a 4-day lag to regain lost time.",
    "Cost Performance Index (CPI) is 0.94. Main variance is localized in foundation excavation rates. Re-level skilled masonry crews to control overtime charges."
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8 text-left"
    >
      {/* Top Welcome Banner & Project Selector */}
      <motion.div variants={itemVariants} className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight">
              Executive Dashboard
            </h1>
            <Badge variant="success" className="rounded-full font-bold text-[9px] uppercase tracking-wider py-0.5 px-2 bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
              Live Audits
            </Badge>
          </div>
          <p className="text-xs text-zinc-400 font-medium">
            Welcome back! Active civil controls audit calculations are up to date.
          </p>
        </div>

        {/* Project Dropdown Selector */}
        <div className="flex items-center space-x-2.5">
          <FolderGit2 className="h-5 w-5 text-zinc-500 flex-shrink-0" />
          <select
            value={activeProject?.id || ''}
            onChange={(e) => {
              const proj = projects.find(p => p.id === e.target.value);
              if (proj) selectProject(proj);
            }}
            className="h-10 bg-surface border border-border rounded-xl px-4 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer w-64 shadow-md"
          >
            {projects.length === 0 && <option value="">Loading Projects...</option>}
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Row 1: AI Insights typewriter */}
      <motion.div variants={itemVariants}>
        <AIInsightCard 
          title="Neural Schedule Diagnostics" 
          insights={aiInsightsList} 
        />
      </motion.div>

      {/* Row 2: 6 KPI Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <KPICard 
          title="Schedule Index (SPI)" 
          value="0.91" 
          numericValue={0.91}
          trend="-0.02" 
          trendDirection="down" 
          icon={TrendingDown} 
          color="secondary"
          sparklineData={[0.95, 0.94, 0.93, 0.92, 0.91]}
        />
        <KPICard 
          title="Cost Index (CPI)" 
          value="0.94" 
          numericValue={0.94}
          trend="+0.01" 
          trendDirection="up" 
          icon={TrendingUp} 
          color="primary"
          sparklineData={[0.92, 0.93, 0.93, 0.94, 0.94]}
        />
        <KPICard 
          title="Planned Progress" 
          value="42.0%" 
          numericValue={42.0}
          trend="+5.2%" 
          trendDirection="up" 
          icon={CalendarDays} 
          color="warning"
          sparklineData={[10, 20, 28, 35, 42]}
        />
        <KPICard 
          title="Actual Progress" 
          value="36.0%" 
          numericValue={36.0}
          trend="+4.8%" 
          trendDirection="up" 
          icon={CheckSquare} 
          color="success"
          sparklineData={[8, 16, 22, 30, 36]}
        />
        <KPICard 
          title="Critical Tasks" 
          value="12" 
          numericValue={12}
          trend="Constant" 
          trendDirection="neutral" 
          icon={AlertOctagon} 
          color="danger"
          sparklineData={[12, 12, 12, 12, 12]}
        />
        <KPICard 
          title="Total Float" 
          value="4 days" 
          numericValue={4}
          trend="-2 days" 
          trendDirection="down" 
          icon={Clock} 
          color="warning"
          sparklineData={[6, 6, 5, 4, 4]}
        />
      </motion.div>

      {/* Row 3: Charts side-by-side */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SCurveChart />
        <ResourceHistogram />
      </motion.div>

      {/* Row 4: Watchlist Table and Logs side-by-side */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CriticalActivitiesTable />
        </div>
        <div className="lg:col-span-1">
          <ActivityTimeline />
        </div>
      </motion.div>

      {/* Row 5: Circular gauge */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ProjectHealthScore score={74} className="md:col-span-1" />
        <div className="md:col-span-2 bg-surface border border-white/5 rounded-2xl p-6 flex flex-col justify-center space-y-4">
          <h4 className="text-base font-bold text-white tracking-tight">Project Summary</h4>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Active Project **{activeProject?.name || 'Metro Line Extension'}** (Location: {activeProject?.location || 'Lahore'}). 
            Calculated completion slips are localized around substructure excavation limits. 
            AI forecasting indicates that with the implementation of a 2-hour daily overtime schedule on formwork, 
            the final milestone can be pulled back by 6 days, securing a final completion index of 0.98.
          </p>
          <div className="flex flex-wrap gap-2.5 pt-2">
            <span className="text-[10px] font-bold text-zinc-500 bg-white/3 border border-white/5 rounded-lg px-2.5 py-1 uppercase tracking-wider">
              UET Civil Controls Engine v1.0
            </span>
            <span className="text-[10px] font-bold text-zinc-500 bg-white/3 border border-white/5 rounded-lg px-2.5 py-1 uppercase tracking-wider">
              NetworkX Graph Analysis
            </span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
function CheckSquare(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="m9 11 3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  );
}
