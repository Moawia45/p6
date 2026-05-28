/**
 * ConstructMind AI - Auth Pages Layout
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import * as React from 'react';
import Link from 'next/link';
import { Brain } from 'lucide-react';
import { APP_NAME } from '@/lib/constants';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background relative flex flex-col items-center justify-center p-6 select-none overflow-hidden">
      {/* Background ambient glowing rings */}
      <div className="absolute top-[-30%] left-[-20%] h-[100%] w-[80%] rounded-full bg-primary/5 filter blur-[150px] pointer-events-none" />
      <div className="absolute bottom-[-30%] right-[-20%] h-[100%] w-[80%] rounded-full bg-secondary/5 filter blur-[150px] pointer-events-none" />

      <div className="w-full max-w-md flex flex-col items-center space-y-8 z-10">
        {/* Brand Header */}
        <Link href="/" className="flex flex-col items-center space-y-3 group">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center glow-primary transition-transform duration-300 group-hover:scale-105">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <span className="text-xl font-black tracking-tight text-white uppercase tracking-wider">
            {APP_NAME}
          </span>
        </Link>

        {/* Authentication Box */}
        <div className="w-full flex items-center justify-center">
          {children}
        </div>

        {/* Branding Footer */}
        <p className="text-[10px] text-zinc-600 font-bold uppercase tracking-wider">
          UET Taxila Civil Engineering Controls
        </p>
      </div>
    </div>
  );
}
