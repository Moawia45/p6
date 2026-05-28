/**
 * ConstructMind AI - Layout Sidebar
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion } from 'motion/react';
import { 
  LayoutDashboard, 
  FolderKanban, 
  Calendar, 
  Users, 
  FileSpreadsheet, 
  FileText, 
  ShieldAlert, 
  DollarSign, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  Brain,
  Award,
  Phone
} from 'lucide-react';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';
import { cn } from '@/lib/utils';
import { APP_NAME, CREATOR_INFO } from '@/lib/constants';

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { activeProject } = useProjectStore();

  // Extract project ID from URL pathname if activeProject is still loading/hydrating
  const pathSegments = pathname.split('/').filter(Boolean);
  const pathProjectId = pathSegments[0] === 'projects' && pathSegments[1] && pathSegments[1] !== 'new' ? pathSegments[1] : null;
  const currentProjectId = activeProject?.id || pathProjectId;

  // Define navigation items
  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Projects', href: '/projects', icon: FolderKanban },
    { 
      name: 'Schedule / Gantt', 
      href: currentProjectId ? `/projects/${currentProjectId}/schedule` : '/projects', 
      icon: Calendar 
    },
    { 
      name: 'Resources', 
      href: currentProjectId ? `/projects/${currentProjectId}?tab=resources` : '/projects', 
      icon: Users 
    },
    { 
      name: 'BOQ Analysis', 
      href: currentProjectId ? `/projects/${currentProjectId}/boq` : '/projects', 
      icon: FileSpreadsheet 
    },
    { 
      name: 'Delay Analysis', 
      href: currentProjectId ? `/projects/${currentProjectId}?tab=analysis` : '/projects', 
      icon: ShieldAlert 
    },
    { 
      name: 'Reports', 
      href: currentProjectId ? `/projects/${currentProjectId}?tab=reports` : '/projects', 
      icon: FileText 
    },
    { 
      name: 'Cost Controls', 
      href: currentProjectId ? `/projects/${currentProjectId}?tab=costs` : '/projects', 
      icon: DollarSign 
    },
  ];

  return (
    <motion.aside
      animate={{ width: sidebarCollapsed ? 72 : 260 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className="fixed top-0 left-0 bottom-0 z-40 bg-surface border-r border-white/5 flex flex-col overflow-hidden glass"
    >
      {/* Header / Logo */}
      <div className="h-16 flex items-center px-4 border-b border-white/5 overflow-hidden">
        <Link href="/" className="flex items-center space-x-3 select-none">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center glow-primary">
            <Brain className="h-5 w-5 text-white" />
          </div>
          {!sidebarCollapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-base font-bold bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent tracking-tight whitespace-nowrap"
            >
              {APP_NAME}
            </motion.span>
          )}
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto overflow-x-hidden">
        {menuItems.map((item) => {
          const Icon = item.icon;
          // Check if active: exact match or starts with route path
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center space-x-3 px-3 py-3 rounded-xl text-sm font-medium transition-all duration-200 select-none relative',
                isActive 
                  ? 'text-white bg-white/5 border border-white/5' 
                  : 'text-zinc-400 hover:text-white hover:bg-white/2'
              )}
            >
              {isActive && (
                <motion.div
                  layoutId="activeNavIndicator"
                  className="absolute left-0 top-2 bottom-2 w-1 bg-primary rounded-r"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
              <Icon className={cn('h-5 w-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-105', isActive ? 'text-primary' : 'text-zinc-500 group-hover:text-zinc-300')} />
              {!sidebarCollapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="whitespace-nowrap"
                >
                  {item.name}
                </motion.span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Creator Info Footer */}
      <div className="border-t border-white/5 p-4 bg-surface-2/40 overflow-hidden flex flex-col justify-end">
        {!sidebarCollapsed ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-2 text-left"
          >
            <div className="flex items-center space-x-2">
              <Award className="h-4 w-4 text-primary flex-shrink-0" />
              <p className="text-xs font-semibold text-white truncate">
                {CREATOR_INFO.name}
              </p>
            </div>
            <p className="text-[10px] text-zinc-500 leading-none">
              {CREATOR_INFO.title} • {CREATOR_INFO.institution}
            </p>
            <div className="flex items-center space-x-1.5 pt-1 border-t border-white/5 mt-1.5">
              <Phone className="h-3 w-3 text-zinc-500 flex-shrink-0" />
              <p className="text-[10px] text-zinc-400 font-medium">
                {CREATOR_INFO.phone}
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="flex justify-center py-2">
            <Award className="h-5 w-5 text-primary animate-pulse" />
          </div>
        )}
      </div>

      {/* Collapse Toggle Button */}
      <button
        onClick={toggleSidebar}
        className="h-12 border-t border-white/5 hover:bg-white/2 flex items-center justify-center text-zinc-500 hover:text-white transition-colors"
      >
        {sidebarCollapsed ? (
          <ChevronRight className="h-5 w-5 animate-float" />
        ) : (
          <div className="flex items-center space-x-2 text-xs font-medium uppercase tracking-wider">
            <ChevronLeft className="h-4 w-4" />
            <span>Collapse Menu</span>
          </div>
        )}
      </button>
    </motion.aside>
  );
}
