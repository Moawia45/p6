/**
 * ConstructMind AI - Badge Component
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary/10 text-primary-foreground border-primary/20',
        success: 'border-transparent bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        warning: 'border-transparent bg-amber-500/10 text-amber-400 border-amber-500/20',
        danger: 'border-transparent bg-rose-500/10 text-rose-400 border-rose-500/20',
        info: 'border-transparent bg-sky-500/10 text-sky-400 border-sky-500/20',
        zinc: 'border-transparent bg-zinc-500/10 text-zinc-400 border-zinc-500/20',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

function Badge({ className, variant, dot = false, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span
          className={cn(
            'mr-1.5 h-1.5 w-1.5 rounded-full',
            variant === 'success' && 'bg-emerald-400',
            variant === 'warning' && 'bg-amber-400',
            variant === 'danger' && 'bg-rose-400',
            variant === 'info' && 'bg-sky-400',
            (variant === 'default' || !variant) && 'bg-primary',
            variant === 'zinc' && 'bg-zinc-400'
          )}
        />
      )}
      {props.children}
    </div>
  );
}

export { Badge, badgeVariants };
