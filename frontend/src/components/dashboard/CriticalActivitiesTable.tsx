/**
 * ConstructMind AI - Critical Activities Table Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { AlertTriangle, Clock, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../shared/Card';
import { Badge } from '../shared/Badge';
import { cn, formatDate } from '@/lib/utils';

interface TableActivity {
  id: string;
  activity_id: string;
  name: string;
  duration: number;
  start: string;
  end: string;
  total_float: number;
  status: string;
}

interface CriticalActivitiesTableProps {
  activities?: TableActivity[];
}

export function CriticalActivitiesTable({
  activities = [
    { id: '1', activity_id: 'A1030', name: 'Submit Structural Drawings for Approval', duration: 10, start: '2026-06-08', end: '2026-06-18', total_float: 0, status: 'in_progress' },
    { id: '2', activity_id: 'A2010', name: 'Excavation & Earthwork (GF)', duration: 8, start: '2026-06-18', end: '2026-06-26', total_float: 0, status: 'not_started' },
    { id: '3', activity_id: 'A2020', name: 'Laying Lean Concrete (Substructure)', duration: 4, start: '2026-06-26', end: '2026-06-30', total_float: 0, status: 'not_started' },
    { id: '4', activity_id: 'A2030', name: 'Footings Rebar Fixing & Shuttering', duration: 10, start: '2026-06-30', end: '2026-07-10', total_float: 3, status: 'not_started' }, // near critical
    { id: '5', activity_id: 'A3010', name: 'GF Columns Steel Reinforcement', duration: 8, start: '2026-07-15', end: '2026-07-23', total_float: 0, status: 'not_started' },
  ],
}: CriticalActivitiesTableProps) {
  return (
    <Card className="w-full border-white/5">
      <CardHeader className="pb-3 text-left flex flex-row items-center justify-between">
        <div className="space-y-1">
          <CardTitle className="text-base font-bold">Critical Path Watchlist</CardTitle>
          <CardDescription>Tasks with zero or low float demanding immediate attention</CardDescription>
        </div>
        <div className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-danger/10 border border-danger/20 text-xs text-danger font-bold">
          <AlertTriangle className="h-3.5 w-3.5" />
          <span>CPM Critical</span>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="w-full overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="border-b border-white/5 text-[10px] font-bold text-zinc-500 uppercase tracking-widest bg-white/2">
                <th className="py-3 px-6">ID</th>
                <th className="py-3 px-4">Activity Name</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Early Dates</th>
                <th className="py-3 px-4">Total Float</th>
                <th className="py-3 px-6 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/2">
              {activities.map((act) => {
                const isCritical = act.total_float === 0;
                const isNearCritical = act.total_float > 0 && act.total_float <= 3;
                
                return (
                  <tr 
                    key={act.id} 
                    className={cn(
                      'hover:bg-white/1.5 transition-colors',
                      isCritical && 'bg-danger/1'
                    )}
                  >
                    <td className="py-3.5 px-6 font-mono font-bold text-zinc-400">
                      {act.activity_id}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-white max-w-[280px] truncate">
                      {act.name}
                    </td>
                    <td className="py-3.5 px-4 text-zinc-300">
                      {act.duration} days
                    </td>
                    <td className="py-3.5 px-4 text-zinc-400">
                      <div className="flex items-center space-x-1">
                        <span>{formatDate(act.start)}</span>
                        <ArrowRight className="h-3 w-3 text-zinc-600" />
                        <span>{formatDate(act.end)}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      {isCritical ? (
                        <Badge variant="danger" dot>0 days</Badge>
                      ) : isNearCritical ? (
                        <Badge variant="warning" dot>{act.total_float} days</Badge>
                      ) : (
                        <Badge variant="zinc" dot>{act.total_float} days</Badge>
                      )}
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      <span className={cn(
                        'px-2.5 py-0.5 rounded-full text-[10px] font-bold border capitalize',
                        act.status === 'in_progress' && 'bg-blue-500/10 border-blue-500/20 text-blue-400',
                        act.status === 'not_started' && 'bg-zinc-500/10 border-zinc-500/20 text-zinc-400',
                        act.status === 'completed' && 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                      )}>
                        {act.status.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
export default CriticalActivitiesTable;
