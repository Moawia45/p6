/**
 * ConstructMind AI - Activity Timeline Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { Play, Award, FileSpreadsheet, Sparkles, CheckSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../shared/Card';
import { cn } from '@/lib/utils';

interface TimelineItem {
  id: string;
  time: string;
  user: string;
  action: string;
  icon: any;
  color: string;
}

interface ActivityTimelineProps {
  items?: TimelineItem[];
}

export function ActivityTimeline({
  items = [
    { id: '1', time: '10 mins ago', user: 'Moawia Husnain', action: 'Ran schedule CPM forward/backward date calculations', icon: Play, color: 'bg-primary border-primary/20 text-primary' },
    { id: '2', time: '1 hour ago', user: 'Moawia Husnain', action: 'Uploaded and analyzed Bill of Quantities Excel', icon: FileSpreadsheet, color: 'bg-accent border-accent/20 text-accent' },
    { id: '3', time: '3 hours ago', user: 'AI Copilot', action: 'Completed duration estimations on GF Columns', icon: Sparkles, color: 'bg-secondary border-secondary/20 text-secondary' },
    { id: '4', time: 'Yesterday', user: 'Moawia Husnain', action: 'Set Metro Segment 4 Schedule baseline snapshot', icon: Award, color: 'bg-amber-500/10 border-amber-500/20 text-amber-400' },
  ],
}: ActivityTimelineProps) {
  return (
    <Card className="w-full border-white/5">
      <CardHeader className="pb-3 text-left">
        <CardTitle className="text-base font-bold">Recent Audits & Logs</CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <div className="relative border-l border-white/5 pl-6 space-y-6">
          {items.map((item, idx) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.1 }}
                className="relative text-left"
              >
                {/* Timeline node icon */}
                <div className={cn(
                  'absolute -left-[35px] top-0.5 h-6.5 w-6.5 rounded-lg flex items-center justify-center border text-[10px]',
                  item.color
                )}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
                
                {/* Details */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">
                      {item.user}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-medium">
                      {item.time}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400">
                    {item.action}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
export default ActivityTimeline;
