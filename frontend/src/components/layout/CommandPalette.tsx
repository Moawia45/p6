/**
 * ConstructMind AI - Command Palette Menu
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Folder, Calendar, Users, Sparkles, FileText, Terminal, Play, LogOut } from 'lucide-react';
import { useUIStore } from '@/store/ui-store';
import { useProjectStore } from '@/store/project-store';
import { useCopilotStore } from '@/store/copilot-store';
import { cn } from '@/lib/utils';

interface CommandItem {
  id: string;
  name: string;
  category: 'Navigation' | 'Quick Actions' | 'AI Controls';
  icon: any;
  shortcut?: string[];
  action: () => void;
}

export function CommandPalette() {
  const router = useRouter();
  const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore();
  const { activeProject } = useProjectStore();
  const { setOpen: setCopilotOpen } = useCopilotStore();

  const [query, setQuery] = React.useState('');
  const [selectedIndex, setSelectedIndex] = React.useState(0);

  // Shortcut binding: Cmd+K / Ctrl+K to toggle palette
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  // Define commands
  const commands: CommandItem[] = [
    // Navigation
    { id: 'nav-dash', name: 'Go to Dashboard', category: 'Navigation', icon: Folder, action: () => { router.push('/dashboard'); setCommandPaletteOpen(false); } },
    { id: 'nav-proj', name: 'Go to Projects List', category: 'Navigation', icon: Folder, action: () => { router.push('/projects'); setCommandPaletteOpen(false); } },
    { id: 'nav-sched', name: 'Go to Schedule / Gantt', category: 'Navigation', icon: Calendar, action: () => { router.push(activeProject ? `/projects/${activeProject.id}/schedule` : '/schedule'); setCommandPaletteOpen(false); } },
    { id: 'nav-res', name: 'Go to Resource Allocation', category: 'Navigation', icon: Users, action: () => { router.push(activeProject ? `/projects/${activeProject.id}?tab=resources` : '/projects'); setCommandPaletteOpen(false); } },
    { id: 'nav-boq', name: 'Go to Bill of Quantities (BOQ)', category: 'Navigation', icon: FileText, action: () => { router.push(activeProject ? `/projects/${activeProject.id}/boq` : '/boq'); setCommandPaletteOpen(false); } },
    
    // Quick Actions
    { id: 'act-cpm', name: 'Run Critical Path CPM Analysis', category: 'Quick Actions', icon: Play, shortcut: ['⌘', 'R'], action: () => { if (activeProject) { router.push(`/projects/${activeProject.id}/schedule?runCPM=true`); } else { router.push('/projects'); } setCommandPaletteOpen(false); } },
    
    // AI controls
    { id: 'ai-copilot', name: 'Ask AI Copilot (Toggle Panel)', category: 'AI Controls', icon: Sparkles, shortcut: ['⌘', 'J'], action: () => { setCopilotOpen(true); setCommandPaletteOpen(false); } },
  ];

  // Filter commands by search string
  const filtered = commands.filter((c) =>
    c.name.toLowerCase().includes(query.toLowerCase()) ||
    c.category.toLowerCase().includes(query.toLowerCase())
  );

  // Keyboard navigation inside list
  React.useEffect(() => {
    if (!commandPaletteOpen) return;
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filtered.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selectedIndex]) {
          filtered[selectedIndex].action();
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        setCommandPaletteOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, filtered, selectedIndex, setCommandPaletteOpen]);

  // Reset indices on query change
  React.useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Handle click on backdrop
  if (!commandPaletteOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4">
        {/* Backdrop overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setCommandPaletteOpen(false)}
          className="absolute inset-0 bg-background/85 backdrop-blur-md"
        />

        {/* Command Menu Box */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97, y: -20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.97, y: -20 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-xl bg-surface border border-white/5 shadow-2xl rounded-2xl overflow-hidden z-10 flex flex-col glass-strong"
        >
          {/* Search Input */}
          <div className="flex items-center px-4 border-b border-white/5">
            <Search className="h-5 w-5 text-zinc-500 mr-3 flex-shrink-0" />
            <input
              type="text"
              placeholder="Type a command or page name..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full h-14 bg-transparent text-sm text-foreground focus:outline-none placeholder:text-zinc-500"
              autoFocus
            />
          </div>

          {/* Commands List */}
          <div className="max-h-[350px] overflow-y-auto p-2">
            {filtered.length > 0 ? (
              <div className="space-y-4">
                {/* Categorized grouping */}
                {['Navigation', 'Quick Actions', 'AI Controls'].map((cat) => {
                  const items = filtered.filter((i) => i.category === cat);
                  if (items.length === 0) return null;

                  return (
                    <div key={cat} className="space-y-1">
                      <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider px-3 py-1 text-left">
                        {cat}
                      </p>
                      {items.map((item) => {
                        const globalIndex = filtered.indexOf(item);
                        const isSelected = globalIndex === selectedIndex;
                        const Icon = item.icon;

                        return (
                          <button
                            key={item.id}
                            onClick={() => item.action()}
                            className={cn(
                              'w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-left transition-all duration-150',
                              isSelected 
                                ? 'bg-primary text-white shadow-md shadow-primary/10' 
                                : 'text-zinc-400 hover:text-white hover:bg-white/2'
                            )}
                          >
                            <div className="flex items-center space-x-3">
                              <Icon className={cn('h-4.5 w-4.5', isSelected ? 'text-white' : 'text-zinc-500')} />
                              <span>{item.name}</span>
                            </div>
                            {item.shortcut && (
                              <div className="flex space-x-0.5">
                                {item.shortcut.map((s, idx) => (
                                  <kbd
                                    key={idx}
                                    className={cn(
                                      'px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border',
                                      isSelected 
                                        ? 'bg-primary-hover border-white/20 text-white' 
                                        : 'bg-white/5 border-white/10 text-zinc-500'
                                    )}
                                  >
                                    {s}
                                  </kbd>
                                ))}
                              </div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center text-center space-y-2">
                <Terminal className="h-8 w-8 text-zinc-500 animate-pulse" />
                <p className="text-xs text-zinc-500 font-medium">
                  No matching console commands found.
                </p>
              </div>
            )}
          </div>
          
          {/* Footer Guide */}
          <div className="h-9 px-4 border-t border-white/5 bg-surface-2/40 flex items-center justify-between text-[10px] text-zinc-500">
            <span className="flex items-center space-x-1">
              <span>↑↓ Navigation</span>
              <span className="mx-1">•</span>
              <span>Enter to run</span>
            </span>
            <span>Esc to close</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
