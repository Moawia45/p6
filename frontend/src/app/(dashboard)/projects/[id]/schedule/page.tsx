/**
 * ConstructMind AI - Interactive Gantt Schedule & CPM controls
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { motion } from 'motion/react';
import { 
  Play, 
  Plus, 
  Trash2, 
  Save, 
  Settings, 
  Layers, 
  Sparkles,
  CalendarDays,
  Info,
  Link2,
  ChevronDown
} from 'lucide-react';
import { useScheduleStore } from '@/store/schedule-store';
import { useProjectStore } from '@/store/project-store';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { Badge } from '@/components/shared/Badge';
import { Input } from '@/components/shared/Input';
import { Modal } from '@/components/shared/Modal';
import { formatCurrency, formatDate } from '@/lib/utils';
import { ACTIVITY_TYPES, RELATIONSHIP_TYPES } from '@/lib/constants';

export default function SchedulePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = params.id as string;
  const runCPMOnLoad = searchParams.get('runCPM') === 'true';

  const { activeProject } = useProjectStore();
  const { 
    ganttData, 
    activities, 
    fetchGanttData, 
    fetchActivities, 
    calculateCPM, 
    createActivity, 
    updateActivity, 
    deleteActivity,
    createRelationship,
    loading 
  } = useScheduleStore();

  const [selectedActivityId, setSelectedActivityId] = React.useState<string | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = React.useState(false);
  const [isCPMRunning, setIsCPMRunning] = React.useState(false);
  
  // Create Form State
  const [actId, setActId] = React.useState('');
  const [actName, setActName] = React.useState('');
  const [actType, setActType] = React.useState('task');
  const [actDuration, setActDuration] = React.useState(5);
  const [actQuantity, setActQuantity] = React.useState(0);
  const [actUnit, setActUnit] = React.useState('LS');

  // Load Gantt Data
  React.useEffect(() => {
    if (projectId) {
      fetchGanttData(projectId);
      fetchActivities(projectId);
    }
  }, [projectId, fetchGanttData, fetchActivities]);

  // Handle URL CPM trigger
  React.useEffect(() => {
    if (runCPMOnLoad && activeProject && activities.length > 0 && !isCPMRunning) {
      handleRunCPM();
    }
  }, [runCPMOnLoad, activeProject, activities]);

  const handleRunCPM = async () => {
    if (!activeProject) return;
    setIsCPMRunning(true);
    const startStr = activeProject.planned_start || new Date().toISOString().split('T')[0];
    
    await calculateCPM(projectId, startStr, activeProject.calendar_type, activeProject.hours_per_day);
    setIsCPMRunning(false);
  };

  const handleSaveActivity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actId.trim() || !actName.trim()) return;

    const payload = {
      activity_id: actId,
      name: actName,
      activity_type: actType,
      original_duration: Number(actDuration),
      quantity: Number(actQuantity),
      unit: actUnit,
      wbs_id: null,
      planned_start: activeProject?.planned_start || new Date().toISOString().split('T')[0]
    };

    await createActivity(projectId, payload);
    setIsCreateModalOpen(false);
    
    // Clear
    setActId('');
    setActName('');
    setActDuration(5);
  };

  const selectedActivity = activities.find(a => a.id === selectedActivityId);

  // Compute timeline parameters
  // Find project bounds (earliest start, latest finish)
  const getProjectBounds = () => {
    const dates = activities
      .map(a => [a.planned_start || a.early_start, a.planned_finish || a.early_finish])
      .flat()
      .filter(Boolean) as string[];

    if (dates.length === 0) return { start: new Date(), end: new Date(Date.now() + 30 * 86400000) };
    
    const parsed = dates.map(d => new Date(d));
    return {
      start: new Date(Math.min(...parsed.map(p => p.getTime()))),
      end: new Date(Math.max(...parsed.map(p => p.getTime())))
    };
  };

  const bounds = getProjectBounds();
  const totalDays = Math.ceil((bounds.end.getTime() - bounds.start.getTime()) / 86400000) + 7; // add padding week

  const getPercentageWidthAndLeft = (startStr?: string, finishStr?: string) => {
    if (!startStr || !finishStr) return { left: 0, width: 0 };
    
    const start = new Date(startStr);
    const finish = new Date(finishStr);
    
    const leftDays = (start.getTime() - bounds.start.getTime()) / 86400000;
    const durationDays = (finish.getTime() - start.getTime()) / 86400000;
    
    const leftPercent = (leftDays / totalDays) * 100;
    const widthPercent = (durationDays / totalDays) * 100;
    
    return {
      left: Math.max(0, leftPercent),
      width: Math.max(1, widthPercent) // minimum 1% width
    };
  };

  return (
    <div className="space-y-8 text-left">
      {/* Top action header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center space-x-2.5">
            <span>Scheduling Console</span>
          </h1>
          <p className="text-xs text-zinc-400 font-medium">
            Interactive CPM scheduler, calendar adjustments, and logic dependencies.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleRunCPM}
            isLoading={isCPMRunning}
            className="border-primary/30 text-primary hover:bg-primary/5 rounded-xl glow-primary font-bold"
          >
            <Play className="h-4.5 w-4.5 mr-2" />
            <span>Calculate CPM</span>
          </Button>

          <Button
            variant="primary"
            onClick={() => setIsCreateModalOpen(true)}
            className="rounded-xl flex items-center space-x-2 shadow-lg shadow-primary/20 glow-primary font-bold h-11"
          >
            <Plus className="h-5 w-5" />
            <span>Add Activity</span>
          </Button>
        </div>
      </div>

      {/* Grid: Schedule left table / right timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Left Side: Table & Timeline */}
        <div className="lg:col-span-3 space-y-6">
          <Card className="border-white/5 p-0 overflow-hidden flex flex-col">
            {/* Timeline Header Row */}
            <div className="p-4 border-b border-white/5 bg-white/2 flex justify-between items-center text-xs">
              <div className="flex items-center space-x-2 text-zinc-400 font-semibold">
                <CalendarDays className="h-4.5 w-4.5 text-zinc-500" />
                <span>Gantt Chart Workspace</span>
              </div>
              <div className="flex items-center space-x-3 text-[10px] uppercase font-bold text-zinc-500">
                <span className="flex items-center space-x-1">
                  <span className="h-2.5 w-2.5 bg-danger rounded-full" />
                  <span>Critical (0 Float)</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span className="h-2.5 w-2.5 bg-primary rounded-full" />
                  <span>Non-critical</span>
                </span>
              </div>
            </div>

            {/* Split layout: Table details (left) + Graphic timeline bars (right) */}
            <div className="flex w-full overflow-x-auto min-h-[400px]">
              {/* Left pane: Tree list (fixed width) */}
              <div className="w-[380px] border-r border-white/5 flex-shrink-0">
                <table className="w-full text-xs text-left border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-[9px] font-bold text-zinc-500 uppercase tracking-wider bg-white/1.5 h-10">
                      <th className="py-2 px-4">ID</th>
                      <th className="py-2 px-2">Activity Name</th>
                      <th className="py-2 px-2 text-right">Dur</th>
                      <th className="py-2 px-2 text-center">Float</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/2">
                    {activities.map((act) => {
                      const isSelected = act.id === selectedActivityId;
                      return (
                        <tr 
                          key={act.id} 
                          onClick={() => setSelectedActivityId(act.id)}
                          className={cn(
                            'hover:bg-white/1.5 transition-colors cursor-pointer h-12',
                            isSelected && 'bg-white/5 border-l-2 border-primary',
                            act.is_critical && 'bg-danger/1'
                          )}
                        >
                          <td className="py-2 px-4 font-mono font-bold text-zinc-400">
                            {act.activity_id}
                          </td>
                          <td className="py-2 px-2 font-semibold text-white truncate max-w-[180px]">
                            {act.name}
                          </td>
                          <td className="py-2 px-2 text-right text-zinc-300 font-medium">
                            {act.original_duration}d
                          </td>
                          <td className="py-2 px-2 text-center">
                            {act.is_critical ? (
                              <span className="text-danger font-bold">0d</span>
                            ) : (
                              <span className="text-zinc-500">{act.total_float}d</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Right pane: Timeline bars (scrollable horizontally) */}
              <div className="flex-1 min-w-[500px] relative">
                {/* Timeline Grid Background Lines */}
                <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:10%_100%] pointer-events-none" />

                {/* Header timeline dates */}
                <div className="h-10 border-b border-white/5 bg-white/1.5 flex items-center justify-between px-3 text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  <span>{formatDate(bounds.start)}</span>
                  <span>Timeline Frame</span>
                  <span>{formatDate(bounds.end)}</span>
                </div>

                {/* Timeline activity bars */}
                <div className="divide-y divide-white/2">
                  {activities.map((act) => {
                    const isSelected = act.id === selectedActivityId;
                    const { left, width } = getPercentageWidthAndLeft(
                      act.planned_start || act.early_start,
                      act.planned_finish || act.early_finish
                    );
                    const isMilestone = act.activity_type === 'milestone' || 
                                        (act.activity_type && typeof act.activity_type === 'object' && act.activity_type.value === 'milestone');

                    return (
                      <div 
                        key={act.id}
                        onClick={() => setSelectedActivityId(act.id)}
                        className={cn(
                          'h-12 relative flex items-center cursor-pointer transition-colors hover:bg-white/1.5',
                          isSelected && 'bg-white/5'
                        )}
                      >
                        {isMilestone ? (
                          /* Milestone diamond */
                          <div 
                            style={{ left: `${left}%` }}
                            className="absolute h-3.5 w-3.5 bg-amber-400 border border-amber-500 rotate-45 transform -translate-x-1.5 shadow-md shadow-amber-400/20"
                            title={`${act.name}: ${formatDate(act.planned_start || act.early_start)}`}
                          />
                        ) : (
                          /* Standard duration bar */
                          <div 
                            style={{ left: `${left}%`, width: `${width}%` }}
                            className={cn(
                              'absolute h-5 rounded-md shadow-md border flex items-center justify-end px-2 text-[8px] font-black text-white select-none',
                              act.is_critical 
                                ? 'bg-gradient-to-r from-danger to-rose-400 border-danger/30 shadow-danger/10' 
                                : 'bg-gradient-to-r from-primary to-secondary border-primary/20 shadow-primary/10'
                            )}
                            title={`${act.name}: ${act.original_duration} days (${act.planned_start} to ${act.planned_finish})`}
                          >
                            {width > 12 && <span>{act.original_duration}d</span>}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Side: Activity details panel */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="border-white/5">
            <CardHeader className="pb-3 text-left">
              <CardTitle className="text-sm font-bold">Activity Properties</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-xs text-left">
              {selectedActivity ? (
                <div className="space-y-4">
                  <div className="space-y-1">
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Activity ID</p>
                    <p className="text-sm font-bold text-white font-mono">{selectedActivity.activity_id}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Activity Name</p>
                    <p className="text-xs text-zinc-300 font-semibold">{selectedActivity.name}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Duration</p>
                      <p className="text-xs text-white font-bold">{selectedActivity.original_duration} working days</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Total Float</p>
                      <p className={cn(
                        'text-xs font-black',
                        selectedActivity.is_critical ? 'text-danger' : 'text-zinc-400'
                      )}>
                        {selectedActivity.total_float} days
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Early Start</p>
                      <p className="text-xs text-zinc-400 font-bold">{formatDate(selectedActivity.early_start)}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Early Finish</p>
                      <p className="text-xs text-zinc-400 font-bold">{formatDate(selectedActivity.early_finish)}</p>
                    </div>
                  </div>
                  
                  <div className="h-px bg-white/5 my-2" />

                  {/* Danger zone details */}
                  {selectedActivity.is_critical && (
                    <div className="bg-danger/10 border border-danger/25 text-danger p-3.5 rounded-xl flex items-start space-x-2.5">
                      <Info className="h-4.5 w-4.5 mt-0.5 flex-shrink-0" />
                      <p className="text-[10px] leading-normal text-zinc-400 font-medium">
                        This activity lies on the **Critical Path**. Any delay will delay the project final finish milestone.
                      </p>
                    </div>
                  )}

                  {/* Delete button */}
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={async () => {
                      if (confirm('Delete this activity?')) {
                        await deleteActivity(projectId, selectedActivity.id);
                        setSelectedActivityId(null);
                      }
                    }}
                    className="w-full rounded-xl flex items-center justify-center space-x-2"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>Delete Task</span>
                  </Button>
                </div>
              ) : (
                <div className="py-12 flex flex-col items-center justify-center text-center space-y-2 text-zinc-500">
                  <Info className="h-8 w-8 text-zinc-600 animate-pulse" />
                  <p className="text-xs font-semibold leading-relaxed max-w-[150px]">
                    Select an activity row to view calendar dates, float, and properties.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Activity Create Modal Form */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Activity"
        className="max-w-md"
      >
        <form onSubmit={handleSaveActivity} className="space-y-4 text-left">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Activity ID (e.g. A1050)"
              placeholder="A1050"
              value={actId}
              onChange={(e) => setActId(e.target.value)}
              required
              className="bg-surface-2 border-white/5"
            />
            <Input
              label="Duration (Days)"
              type="number"
              value={actDuration}
              onChange={(e) => setActDuration(Number(e.target.value))}
              required
              className="bg-surface-2 border-white/5"
            />
          </div>

          <Input
            label="Activity Name / Description"
            placeholder="Pouring RCCGF Slab concrete"
            value={actName}
            onChange={(e) => setActName(e.target.value)}
            required
            className="bg-surface-2 border-white/5"
          />

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1.5 flex flex-col col-span-1">
              <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Type</label>
              <select
                value={actType}
                onChange={(e) => setActType(e.target.value)}
                className="h-11 bg-surface-2 border border-white/5 rounded-xl px-3.5 text-xs text-white focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {Object.entries(ACTIVITY_TYPES).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div className="col-span-1">
              <Input
                label="Quantity"
                type="number"
                value={actQuantity}
                onChange={(e) => setActQuantity(Number(e.target.value))}
                className="bg-surface-2 border-white/5"
              />
            </div>
            <div className="col-span-1">
              <Input
                label="Unit (UOM)"
                placeholder="m³"
                value={actUnit}
                onChange={(e) => setActUnit(e.target.value)}
                className="bg-surface-2 border-white/5"
              />
            </div>
          </div>

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-white/5">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setIsCreateModalOpen(false)}
              className="text-zinc-400 hover:text-white rounded-xl h-11"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="rounded-xl h-11 shadow-lg px-6"
            >
              Add Task
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
