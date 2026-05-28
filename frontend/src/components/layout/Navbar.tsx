/**
 * ConstructMind AI - Layout Top Navbar
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { usePathname } from 'next/navigation';
import { UserButton, useUser, SignInButton } from '@clerk/nextjs';
import { Bell, Search, Sparkles, Menu } from 'lucide-react';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';
import { useCopilotStore } from '@/store/copilot-store';
import { cn } from '@/lib/utils';
import { Button } from '../shared/Button';

export function Navbar() {
  const pathname = usePathname();
  const { isSignedIn } = useUser();
  const { toggleSidebar, toggleCommandPalette, notificationCount } = useUIStore();
  const { activeProject } = useProjectStore();
  const { toggleOpen: toggleCopilot } = useCopilotStore();

  // Generate breadcrumbs from route path
  const getBreadcrumbs = () => {
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length === 0) return ['ConstructMind', 'Welcome'];
    
    return segments.map((seg, index) => {
      // Decode URL
      let name = decodeURIComponent(seg);
      // Format project UUID to 'Project Details' or project name
      if (name.length > 20 && index === 1) {
        return activeProject ? activeProject.name : 'Project Details';
      }
      // Capitalize first letters
      return name
        .replace(/-/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());
    });
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 sticky top-0 bg-background/50 backdrop-blur-md z-30 select-none">
      {/* Left: Menu toggle and breadcrumbs */}
      <div className="flex items-center space-x-4">
        <button
          onClick={toggleSidebar}
          className="text-zinc-400 hover:text-white p-1.5 hover:bg-white/5 rounded-lg transition-colors md:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-zinc-400">
          {breadcrumbs.map((crumb, idx) => (
            <React.Fragment key={crumb}>
              {idx > 0 && <span className="text-zinc-600">/</span>}
              <span className={cn(idx === breadcrumbs.length - 1 && 'text-primary font-bold')}>
                {crumb}
              </span>
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Right: Quick actions */}
      <div className="flex items-center space-x-3">
        {/* Search / Command Palette Toggle */}
        <button
          onClick={toggleCommandPalette}
          className="h-10 px-3 bg-surface-2/40 border border-white/5 hover:border-white/10 rounded-xl flex items-center justify-between space-x-4 text-xs text-zinc-400 hover:text-zinc-200 transition-all duration-200 w-44 md:w-56"
        >
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4 text-zinc-500" />
            <span>Search console...</span>
          </div>
          <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[10px] font-medium text-zinc-400">
            <span className="text-xs">⌘</span>K
          </kbd>
        </button>

        {/* AI Copilot Toggle */}
        <Button
          variant="outline"
          size="sm"
          onClick={toggleCopilot}
          className="h-10 px-3.5 border-primary/30 text-primary hover:bg-primary/5 rounded-xl flex items-center space-x-1.5 glow-primary"
        >
          <Sparkles className="h-4 w-4 text-primary animate-pulse" />
          <span className="hidden sm:inline">Ask AI Copilot</span>
        </Button>

        {/* Notifications */}
        <button className="relative p-2.5 text-zinc-400 hover:text-white hover:bg-white/5 rounded-xl border border-transparent hover:border-white/5 transition-all duration-200">
          <Bell className="h-5 w-5" />
          {notificationCount > 0 && (
            <span className="absolute top-1.5 right-1.5 h-4 min-w-4 px-1 rounded-full bg-primary flex items-center justify-center text-[10px] font-bold text-white shadow-sm border border-background">
              {notificationCount}
            </span>
          )}
        </button>

        {/* User Account Menu (Clerk) */}
        <div className="pl-1 border-l border-white/5 h-8 flex items-center justify-center">
          {isSignedIn ? (
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "h-8 w-8 rounded-xl border border-white/10"
                }
              }}
            />
          ) : (
            <SignInButton mode="modal">
              <Button variant="primary" size="sm" className="h-8 py-0 px-3 text-xs rounded-lg">
                Sign In
              </Button>
            </SignInButton>
          )}
        </div>
      </div>
    </header>
  );
}
