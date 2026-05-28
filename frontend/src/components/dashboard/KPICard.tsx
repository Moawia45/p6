/**
 * ConstructMind AI - Dashboard KPICard
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { motion } from 'motion/react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Card, CardContent } from '../shared/Card';

interface KPICardProps {
  title: string;
  value: string | number;
  numericValue?: number; // used for counter logic
  trend?: string; // e.g. "+2.5%" or "-1.2%"
  trendDirection?: 'up' | 'down' | 'neutral';
  icon: any; // Lucide Icon
  color?: 'primary' | 'accent' | 'danger' | 'warning' | 'success';
  sparklineData?: number[];
}

export function KPICard({
  title,
  value,
  numericValue,
  trend,
  trendDirection = 'neutral',
  icon: Icon,
  color = 'primary',
  sparklineData = [10, 15, 8, 12, 18, 14, 22],
}: KPICardProps) {
  const [count, setCount] = React.useState(0);

  // Simple count-up effect for numeric values
  React.useEffect(() => {
    if (numericValue === undefined) return;
    
    let start = 0;
    const end = numericValue;
    if (start === end) return;

    const totalDuration = 1000; // 1 second animation
    const incrementTime = 30;
    const totalSteps = totalDuration / incrementTime;
    const stepSize = (end - start) / totalSteps;

    let timer = setInterval(() => {
      start += stepSize;
      if ((stepSize > 0 && start >= end) || (stepSize < 0 && start <= end)) {
        clearInterval(timer);
        setCount(end);
      } else {
        setCount(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [numericValue]);

  // Generate SVG path for sparkline
  const generateSparklinePath = () => {
    if (!sparklineData || sparklineData.length === 0) return '';
    const width = 80;
    const height = 30;
    const minVal = Math.min(...sparklineData);
    const maxVal = Math.max(...sparklineData);
    const range = maxVal - minVal || 1;

    const points = sparklineData.map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * width;
      const y = height - ((val - minVal) / range) * height + 2; // pad 2px top/bottom
      return `${x},${y}`;
    });

    return `M ${points.join(' L ')}`;
  };

  const displayValue = numericValue !== undefined 
    ? (typeof value === 'string' && value.includes('%') ? `${count.toFixed(1)}%` : count.toFixed(2)) 
    : value;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card hoverGlow className="relative overflow-hidden group border-white/5">
        {/* Glow effect on hover */}
        <div className={cn(
          'absolute -top-12 -left-12 h-24 w-24 rounded-full filter blur-xl opacity-0 group-hover:opacity-20 transition-all duration-300 pointer-events-none',
          color === 'primary' && 'bg-primary',
          color === 'accent' && 'bg-accent',
          color === 'danger' && 'bg-danger',
          color === 'warning' && 'bg-warning',
          color === 'success' && 'bg-success'
        )} />

        <CardContent className="p-5 flex flex-col space-y-4 text-left">
          {/* Header row: Icon & Trend */}
          <div className="flex items-center justify-between">
            <div className={cn(
              'h-10 w-10 rounded-xl flex items-center justify-center border',
              color === 'primary' && 'bg-primary/10 border-primary/20 text-primary glow-primary',
              color === 'accent' && 'bg-accent/10 border-accent/20 text-accent',
              color === 'danger' && 'bg-danger/10 border-danger/25 text-danger',
              color === 'warning' && 'bg-warning/10 border-warning/20 text-warning',
              color === 'success' && 'bg-success/10 border-success/20 text-success'
            )}>
              <Icon className="h-5 w-5" />
            </div>

            {/* Trend Indicator */}
            {trend && (
              <div className={cn(
                'flex items-center space-x-0.5 px-2 py-0.5 rounded-full text-[10px] font-bold border',
                trendDirection === 'up' && 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
                trendDirection === 'down' && 'bg-rose-500/10 border-rose-500/25 text-rose-400',
                trendDirection === 'neutral' && 'bg-zinc-500/10 border-zinc-500/20 text-zinc-400'
              )}>
                {trendDirection === 'up' && <ArrowUpRight className="h-3 w-3" />}
                {trendDirection === 'down' && <ArrowDownRight className="h-3 w-3" />}
                {trendDirection === 'neutral' && <Minus className="h-3 w-3" />}
                <span>{trend}</span>
              </div>
            )}
          </div>

          {/* Metric Details */}
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest leading-none">
              {title}
            </p>
            <div className="flex items-baseline justify-between">
              <h2 className="text-2xl font-black text-white tracking-tight">
                {displayValue}
              </h2>

              {/* Mini Sparkline */}
              {sparklineData && sparklineData.length > 0 && (
                <div className="h-6 w-20 flex items-center justify-center opacity-60 group-hover:opacity-100 transition-opacity duration-300">
                  <svg width="80" height="34" className="overflow-visible">
                    <path
                      d={generateSparklinePath()}
                      fill="none"
                      stroke={
                        color === 'primary' ? 'var(--primary)' :
                        color === 'accent' ? 'var(--accent)' :
                        color === 'danger' ? 'var(--danger)' :
                        color === 'warning' ? 'var(--warning)' :
                        'var(--success)'
                      }
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
