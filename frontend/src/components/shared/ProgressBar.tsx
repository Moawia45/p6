/**
 * ConstructMind AI - ProgressBar Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number; // 0 to 100
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  animate?: boolean;
  color?: 'primary' | 'accent' | 'danger' | 'warning' | 'success';
}

export function ProgressBar({
  value,
  showLabel = false,
  size = 'md',
  className,
  animate = true,
  color = 'primary',
}: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value));

  return (
    <div className={cn('w-full space-y-1.5', className)}>
      {showLabel && (
        <div className="flex justify-between items-center text-xs font-semibold text-zinc-400">
          <span>Progress</span>
          <span className="text-foreground">{clampedValue.toFixed(1)}%</span>
        </div>
      )}
      <div
        className={cn(
          'w-full bg-surface-2 rounded-full overflow-hidden border border-white/5',
          size === 'sm' && 'h-1.5',
          size === 'md' && 'h-3',
          size === 'lg' && 'h-5'
        )}
      >
        <div
          style={{ width: `${clampedValue}%` }}
          className={cn(
            'h-full rounded-full transition-all duration-500 ease-out',
            animate && 'bg-gradient-to-r',
            color === 'primary' && 'from-primary to-secondary',
            color === 'accent' && 'from-accent to-emerald-400',
            color === 'danger' && 'from-danger to-rose-400',
            color === 'warning' && 'from-warning to-amber-300',
            color === 'success' && 'from-success to-emerald-400'
          )}
        />
      </div>
    </div>
  );
}
