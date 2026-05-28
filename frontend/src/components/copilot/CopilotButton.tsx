/**
 * ConstructMind AI - Copilot Floating Button
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { Brain } from 'lucide-react';
import { useCopilotStore } from '@/store/copilot-store';
import { cn } from '@/lib/utils';

export function CopilotButton() {
  const { toggleOpen, isOpen } = useCopilotStore();

  // Bind keyboard shortcut Ctrl+J to toggle copilot
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'j') {
        e.preventDefault();
        toggleOpen();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [toggleOpen]);

  if (isOpen) return null;

  return (
    <button
      onClick={toggleOpen}
      title="AI Copilot (Ctrl+J)"
      className="fixed right-6 bottom-6 h-14 w-14 rounded-full bg-gradient-to-tr from-primary to-secondary text-white flex items-center justify-center shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 z-50 glow-primary animate-pulse-glow"
    >
      <Brain className="h-6 w-6 text-white" />
      <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-accent animate-ping" />
      <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-accent" />
    </button>
  );
}
