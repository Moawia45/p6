/**
 * ConstructMind AI - Project Dashboard Hub
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'motion/react';
import { 
  Building, 
  MapPin, 
  DollarSign, 
  Calendar, 
  Users, 
  FileSpreadsheet, 
  Clock, 
  Sparkles,
  ArrowRight,
  TrendingUp,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { useProjectStore } from '@/store/project-store';
import { useScheduleStore } from '@/store/schedule-store';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { Badge } from '@/components/shared/Badge';
import { ProgressBar } from '@/components/shared/ProgressBar';
import { Tabs } from '@/components/shared/Tabs';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = params.id as string;
  const initialTab = searchParams.get('tab') || 'overview';

  const { activeProject, fetchProject } = useProjectStore();
  const { resources, assignments, fetchResources, fetchAssignments } = useScheduleStore();
  const [activeTab, setActiveTab] = React.useState(initialTab);

  React.useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
      fetchResources(projectId);
      fetchAssignments(projectId);
    }
  }, [projectId, fetchProject, fetchResources, fetchAssignments]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'boq') {
      router.push(`/projects/${projectId}/boq`);
    } else if (tabId === 'schedule') {
      router.push(`/projects/${projectId}/schedule`);
    } else {
      router.push(`/projects/${projectId}?tab=${tabId}`);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'boq', label: 'BOQ Analysis', icon: <FileSpreadsheet className="h-4 w-4" /> },
    { id: 'schedule', label: 'Schedule / Gantt', icon: <Calendar className="h-4 w-4" /> },
    { id: 'resources', label: 'Resources' },
    { id: 'analysis', label: 'Delay Analysis' },
    { id: 'reports', label: 'Reports' },
  ];

  if (!activeProject) {
    return (
      <div className="py-24 text-center space-y-4">
        <Clock className="h-8 w-8 text-zinc-500 mx-auto animate-spin" />
        <p className="text-xs text-zinc-400 font-bold uppercase tracking-wider">Syncing project records...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 text-left">
      {/* Page Header */}
      <div className="border-b border-white/5 pb-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center space-x-3">
              <span className="text-[10px] font-mono font-black text-primary tracking-widest leading-none bg-primary/10 border border-primary/20 rounded-md px-2 py-1">
                {activeProject.code || 'CM-PROJ'}
              </span>
              <Badge variant="success" className="capitalize rounded-full font-bold">
                {activeProject.status}
              </Badge>
            </div>
            <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight leading-none">
              {activeProject.name}
            </h1>
            <p className="text-xs text-zinc-400 font-medium">
              {activeProject.description || 'Initialize tasks by uploading a Bill of Quantities spreadsheet.'}
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="primary"
              onClick={() => router.push(`/projects/${projectId}/schedule`)}
              className="rounded-xl flex items-center space-x-2 shadow-lg glow-primary h-11"
            >
              <span>Launch Gantt Timeline</span>
              <ArrowRight className="h-4.5 w-4.5" />
            </Button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <Tabs tabs={tabs} activeTab={activeTab} onChange={handleTabChange} variant="underline" />
      </div>

      {/* Tab Panels */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          {/* Left panel: Core metadata and stats */}
          <div className="lg:col-span-2 space-y-6">
            {/* Project Metrics Summary Card */}
            <Card className="border-white/5">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">Engineering Parameters</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 sm:grid-cols-3 gap-6 text-xs text-zinc-400">
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Client</p>
                  <p className="text-white font-bold mt-1.5 leading-none">{activeProject.client_name || 'N/A'}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Contractor</p>
                  <p className="text-white font-bold mt-1.5 leading-none">{activeProject.contractor_name || 'N/A'}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Contract Value</p>
                  <p className="text-white font-bold mt-1.5 leading-none">
                    {activeProject.budget ? formatCurrency(activeProject.budget, activeProject.currency) : 'N/A'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Location</p>
                  <p className="text-white font-bold mt-1.5 leading-none">{activeProject.location || 'Lahore'}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Start Date</p>
                  <p className="text-white font-bold mt-1.5 leading-none">{formatDate(activeProject.planned_start)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider leading-none">Finish Date</p>
                  <p className="text-white font-bold mt-1.5 leading-none">{formatDate(activeProject.planned_finish)}</p>
                </div>
              </CardContent>
            </Card>

            {/* Milestones Card */}
            <Card className="border-white/5">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">Key Project Milestones</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-xs text-left">
                {[
                  { title: 'Project Mobilization', date: activeProject.planned_start || '2026-06-01', status: 'completed' },
                  { title: 'Foundation Footings Concrete Pour', date: '2026-07-15', status: 'pending' },
                  { title: 'GF Slab Casting Completed', date: '2026-08-09', status: 'pending' },
                  { title: 'Final Handover & Demobilization', date: activeProject.planned_finish || '2026-10-13', status: 'pending' },
                ].map((m, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-surface-2/40 border border-white/5">
                    <div className="flex items-center space-x-3">
                      <span className={cn(
                        'h-3.5 w-3.5 rotate-45 border shadow-sm',
                        m.status === 'completed' ? 'bg-emerald-500 border-emerald-600 shadow-emerald-500/10' : 'bg-zinc-800 border-zinc-700'
                      )} />
                      <span className="font-semibold text-white">{m.title}</span>
                    </div>
                    <span className="text-zinc-400 font-bold">{formatDate(m.date)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right panel: Health score circular donut */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="border-white/5">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">Project Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-5 text-xs text-left">
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                    <span>Overall progress</span>
                    <span className="text-white">35%</span>
                  </div>
                  <ProgressBar value={35} color="success" size="md" />
                </div>
                <div className="h-px bg-white/5 my-2" />
                <div className="flex justify-between items-center text-zinc-500">
                  <span>Total activities:</span>
                  <span className="text-white font-bold">{activeProject.activity_count || 19}</span>
                </div>
                <div className="flex justify-between items-center text-zinc-500">
                  <span>Calculated SPI:</span>
                  <span className="text-emerald-400 font-bold">1.00</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'resources' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          <div className="lg:col-span-2">
            <Card className="border-white/5 p-0">
              <div className="p-4 border-b border-white/5 bg-white/2 flex justify-between items-center text-xs font-semibold text-zinc-400">
                <span>Active Resources Log</span>
              </div>
              <div className="w-full overflow-x-auto">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-[9px] font-bold text-zinc-500 uppercase tracking-widest bg-white/1.5 h-10">
                      <th className="py-2 px-6">ID</th>
                      <th className="py-2 px-4">Resource Name</th>
                      <th className="py-2 px-4">Type</th>
                      <th className="py-2 px-4 text-right">Max Units</th>
                      <th className="py-2 px-6 text-right">Standard Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/2">
                    {resources.map((res) => (
                      <tr key={res.id} className="hover:bg-white/1 transition-colors h-11">
                        <td className="py-2 px-6 font-mono font-bold text-zinc-400">{res.resource_id}</td>
                        <td className="py-2 px-4 font-semibold text-white">{res.name}</td>
                        <td className="py-2 px-4 text-zinc-300 capitalize">{res.resource_type}</td>
                        <td className="py-2 px-4 text-right text-zinc-300">{res.max_units} {res.unit_of_measure}</td>
                        <td className="py-2 px-6 text-right text-white font-bold">{formatCurrency(res.standard_rate)}/hr</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
          <div className="lg:col-span-1">
            <Card className="border-white/5">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-bold">Crew Utilization</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-xs text-left">
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                    <span>Labor crew utilization</span>
                    <span className="text-white">68%</span>
                  </div>
                  <ProgressBar value={68} color="primary" size="sm" />
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-[10px] font-bold text-zinc-500 uppercase tracking-wider">
                    <span>Equipment utilization</span>
                    <span className="text-white">40%</span>
                  </div>
                  <ProgressBar value={40} color="secondary" size="sm" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'analysis' && (
        <Card className="border-white/5">
          <CardHeader className="pb-3 text-left">
            <CardTitle className="text-base font-bold">Delay Attribution Diagnostic</CardTitle>
            <CardDescription>Forensic Time Impact Analysis (TIA)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 text-xs text-left">
            <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 p-4 rounded-xl flex items-start space-x-3">
              <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0 animate-pulse" />
              <div className="space-y-1">
                <h5 className="font-bold text-white">Slippage Detected (8 Days)</h5>
                <p className="text-[10px] text-zinc-400 leading-normal">
                  Total critical path slippage is calculated at 8 working days relative to the target schedule.
                </p>
              </div>
            </div>
            
            <div className="space-y-2.5">
              <h5 className="font-bold text-white uppercase tracking-wider text-[10px] text-zinc-500">Root Cause Decomposition</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-surface-2/45 border border-white/5">
                  <h6 className="font-bold text-white text-xs">Excusable Weather Delay</h6>
                  <p className="text-[10px] text-zinc-500 mt-1">5 days slip during site clearing due to monsoon floods. EOT claim recommended.</p>
                </div>
                <div className="p-4 rounded-xl bg-surface-2/45 border border-white/5">
                  <h6 className="font-bold text-white text-xs">Non-Excusable Mobilization Delay</h6>
                  <p className="text-[10px] text-zinc-500 mt-1">3 days delay due to masonry subcontractor late arrival. Warn contractor.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'reports' && (
        <Card className="border-white/5">
          <CardHeader className="pb-3 text-left">
            <CardTitle className="text-base font-bold">AI Report Generator</CardTitle>
            <CardDescription>Compile executive controls summaries directly to PDF or Excel files</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 text-xs text-left">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { title: 'Weekly Progress Report', desc: 'Narrative summary of completions, SPI, and bottlenecks.' },
                { title: 'EVM Cost Performance Audit', desc: 'Cost variance metrics, BAC, EAC, and budget curves.' },
                { title: 'Delay Claim TIA Document', desc: 'Attribution log with weather and EOT suggestions.' },
              ].map((r, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-surface-2/45 border border-white/5 hover:border-primary/20 transition-all flex flex-col justify-between items-start space-y-4">
                  <div className="space-y-2">
                    <FileText className="h-6 w-6 text-primary" />
                    <h6 className="font-extrabold text-white text-sm">{r.title}</h6>
                    <p className="text-[10px] text-zinc-500 leading-relaxed">{r.desc}</p>
                  </div>
                  <Button variant="outline" size="sm" className="rounded-xl border-white/5 text-zinc-300">
                    Generate
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
export interface AwardProps {
  className?: string;
}
