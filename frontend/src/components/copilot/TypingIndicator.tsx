/**
 * ConstructMind AI - Copilot Typing Indicator
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';

export function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 bg-surface-2/40 border border-white/5 rounded-2xl p-4 self-start max-w-[80%] animate-fade-in">
      <div className="flex space-x-1.5 items-center">
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">
        AI is thinking...
      </span>
    </div>
  );
}
