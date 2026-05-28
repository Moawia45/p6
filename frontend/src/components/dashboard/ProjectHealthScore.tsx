/**
 * ConstructMind AI - Dashboard ProjectHealthScore
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { ShieldCheck, ShieldAlert } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../shared/Card';
import { cn } from '@/lib/utils';

interface ProjectHealthScoreProps {
  score: number; // 0 to 100
  className?: string;
}

export function ProjectHealthScore({ score, className }: ProjectHealthScoreProps) {
  const [animatedScore, setAnimatedScore] = React.useState(0);
  
  const radius = 60;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  React.useEffect(() => {
    const duration = 1200; // 1.2s animation
    const steps = 30;
    const stepTime = duration / steps;
    const increment = score / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        clearInterval(timer);
        setAnimatedScore(score);
      } else {
        setAnimatedScore(current);
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  // Determine color theme based on score
  const getScoreTheme = (val: number) => {
    if (val >= 80) return { text: 'text-emerald-400', stroke: 'stroke-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', status: 'Excellent', icon: ShieldCheck };
    if (val >= 60) return { text: 'text-blue-400', stroke: 'stroke-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20', status: 'Healthy', icon: ShieldCheck };
    if (val >= 40) return { text: 'text-amber-400', stroke: 'stroke-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', status: 'At Risk', icon: ShieldAlert };
    return { text: 'text-rose-400', stroke: 'stroke-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', status: 'Critical', icon: ShieldAlert };
  };

  const theme = getScoreTheme(animatedScore);
  const StatusIcon = theme.icon;

  return (
    <Card className={cn('w-full border-white/5', className)}>
      <CardHeader className="pb-3 text-left">
        <CardTitle className="text-base font-bold">Project Health Score</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center p-6 space-y-5">
        {/* Animated Circle SVG */}
        <div className="relative flex items-center justify-center h-36 w-36">
          <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 140 140">
            {/* Background track circle */}
            <circle
              cx="70"
              cy="70"
              r={radius}
              className="stroke-zinc-800"
              strokeWidth={strokeWidth}
              fill="transparent"
            />
            {/* Foreground progress circle */}
            <motion.circle
              cx="70"
              cy="70"
              r={radius}
              className={theme.stroke}
              strokeWidth={strokeWidth}
              fill="transparent"
              strokeDasharray={circumference}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              strokeLinecap="round"
            />
          </svg>
          {/* Inner circle contents */}
          <div className="absolute flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-white tracking-tight">
              {Math.round(animatedScore)}
            </span>
            <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">
              Health Index
            </span>
          </div>
        </div>

        {/* Status Badge */}
        <div className={cn(
          'flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-semibold',
          theme.bg,
          theme.border,
          theme.text
        )}>
          <StatusIcon className="h-4 w-4" />
          <span>{theme.status} Status</span>
        </div>
      </CardContent>
    </Card>
  );
}
export default ProjectHealthScore;
