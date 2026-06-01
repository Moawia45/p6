/**
 * ConstructMind AI - Projects Directory
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'motion/react';
import { 
  FolderGit2, 
  Plus, 
  Search, 
  MapPin, 
  Building, 
  DollarSign, 
  Calendar, 
  ChevronRight,
  UserCheck
} from 'lucide-react';
import { useProjectStore } from '@/store/project-store';
import { Card, CardContent } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { Badge } from '@/components/shared/Badge';
import { Input } from '@/components/shared/Input';
import { Modal } from '@/components/shared/Modal';
import { ProgressBar } from '@/components/shared/ProgressBar';
import { formatCurrency, formatDate } from '@/lib/utils';

export default function ProjectsPage() {
  const router = useRouter();
  const { projects, createProject, selectProject } = useProjectStore();
  
  const [searchQuery, setSearchQuery] = React.useState('');
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  // New Project Form State
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [code, setCode] = React.useState('');
  const [budget, setBudget] = React.useState(10000000);
  const [location, setLocation] = React.useState('Lahore, Pakistan');
  const [clientName, setClientName] = React.useState('PMTA');
  const [plannedStart, setPlannedStart] = React.useState('2026-06-01');
  const [plannedFinish, setPlannedFinish] = React.useState('2027-02-15');

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (p.code && p.code.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (p.location && p.location.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const payload = {
      name,
      description,
      code: code || `CM-${Math.floor(Math.random() * 900) + 100}`,
      budget: Number(budget),
      location,
      client_name: clientName,
      planned_start: plannedStart,
      planned_finish: plannedFinish,
      calendar_type: '6_day' as any,
      hours_per_day: 8.0,
      status: 'planning' as any,
      currency: 'PKR',
    };

    const newProj = await createProject(payload);
    selectProject(newProj);
    setIsModalOpen(false);
    
    // Clear fields
    setName('');
    setDescription('');
    setCode('');
    
    // Navigate to the newly created project's schedule page for planning
    router.push(`/projects/${newProj.id}/schedule`);
  };

  const getStatusVariant = (status: string) => {
    if (status === 'active') return 'success';
    if (status === 'planning') return 'info';
    if (status === 'on_hold') return 'warning';
    return 'zinc';
  };

  return (
    <div className="space-y-8 text-left">
      {/* Header block */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl md:text-3xl font-black text-white tracking-tight flex items-center space-x-2">
            <span>Projects Directory</span>
          </h1>
          <p className="text-xs text-zinc-400 font-medium">
            Manage your Primavera scheduling baselines and BOQ logs.
          </p>
        </div>
        
        <Button 
          variant="primary" 
          onClick={() => setIsModalOpen(true)}
          className="rounded-xl flex items-center space-x-2 shadow-lg shadow-primary/20 glow-primary h-11 px-5"
        >
          <Plus className="h-5 w-5" />
          <span>New Project</span>
        </Button>
      </div>

      {/* Search Input bar */}
      <div className="flex items-center mb-6">
        <Input
          placeholder="Filter projects by title, code, or location..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          icon={<Search className="h-4.5 w-4.5 text-zinc-500" />}
          className="max-w-md bg-surface-2/40 border-white/5"
        />
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-2">
        {filteredProjects.map((p, idx) => (
          <motion.div
            key={p.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.05 }}
          >
            <Card hoverGlow className="h-full border-white/5 flex flex-col justify-between overflow-hidden relative">
              {/* Accent gradient bar */}
              <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-2xl ${
                p.status === 'active' ? 'bg-gradient-to-b from-emerald-400 to-emerald-600' :
                p.status === 'on_hold' ? 'bg-gradient-to-b from-amber-400 to-amber-600' :
                'bg-gradient-to-b from-primary to-blue-600'
              }`} />
              
              <CardContent className="p-5 pl-6 text-left flex-1 flex flex-col">
                {/* Header: Code + Status */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-[10px] font-mono font-black text-primary tracking-widest bg-primary/10 border border-primary/20 rounded-md px-2 py-1">
                    {p.code || 'CM-PROJ'}
                  </span>
                  <Badge variant={getStatusVariant(p.status)} className="capitalize rounded-full font-bold text-[10px]">
                    {p.status?.replace('_', ' ')}
                  </Badge>
                </div>

                {/* Project Name */}
                <Link href={`/projects/${p.id}/schedule`} onClick={() => selectProject(p)}>
                  <h3 className="text-sm font-extrabold text-white tracking-tight hover:text-primary transition-colors cursor-pointer line-clamp-1 mb-1">
                    {p.name}
                  </h3>
                </Link>
                <p className="text-[11px] text-zinc-500 leading-relaxed line-clamp-2 mb-4">
                  {p.description || 'No project description configured. Upload a BOQ to auto-generate activities.'}
                </p>

                {/* Metrics Grid - Clean Layout */}
                <div className="space-y-3 py-3 border-y border-white/5 mb-4">
                  {/* Budget */}
                  <div className="flex items-center space-x-2.5">
                    <DollarSign className="h-3.5 w-3.5 text-emerald-400 flex-shrink-0" />
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider w-16 flex-shrink-0">Budget</span>
                    <span className="text-xs font-bold text-white">
                      {p.budget ? formatCurrency(p.budget, p.currency) : 'N/A'}
                    </span>
                  </div>
                  {/* Location */}
                  <div className="flex items-center space-x-2.5">
                    <MapPin className="h-3.5 w-3.5 text-blue-400 flex-shrink-0" />
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider w-16 flex-shrink-0">Location</span>
                    <span className="text-xs font-semibold text-zinc-300 truncate">
                      {p.location || 'Pakistan'}
                    </span>
                  </div>
                  {/* Dates */}
                  <div className="flex items-center space-x-2.5">
                    <Calendar className="h-3.5 w-3.5 text-violet-400 flex-shrink-0" />
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider w-16 flex-shrink-0">Period</span>
                    <span className="text-xs text-zinc-300">
                      {formatDate(p.planned_start)}
                      <span className="text-zinc-600 mx-1.5">→</span>
                      {formatDate(p.planned_finish)}
                    </span>
                  </div>
                </div>

                {/* Bottom: Progress / Navigate */}
                <div className="mt-auto flex items-center justify-between">
                  <div className="flex-1 pr-4">
                    {p.status === 'active' ? (
                      <ProgressBar value={35} showLabel size="sm" />
                    ) : (
                      <span className="text-[10px] text-zinc-500 uppercase font-semibold tracking-wider">Planned sequence</span>
                    )}
                  </div>
                  <Link 
                    href={`/projects/${p.id}/schedule`} 
                    onClick={() => selectProject(p)}
                    className="h-8 w-8 rounded-lg bg-white/5 border border-white/5 hover:border-primary/30 hover:bg-primary/10 flex items-center justify-center text-zinc-400 hover:text-primary transition-all flex-shrink-0"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}

        {filteredProjects.length === 0 && (
          <div className="col-span-full py-16 text-center space-y-4 border border-dashed border-white/5 rounded-2xl bg-surface/20">
            <FolderGit2 className="h-10 w-10 text-zinc-500 mx-auto animate-bounce" />
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">No Projects Found</h3>
              <p className="text-xs text-zinc-500 max-w-sm mx-auto leading-relaxed">
                We couldn't find any projects matching your search. Create one to begin AI planning.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Creation Modal Form */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Initialize Construction Project"
        className="max-w-md"
      >
        <form onSubmit={handleCreate} className="space-y-4 text-left">
          <Input
            label="Project Name"
            placeholder="e.g. Metro Line Extension (Segment 4)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="bg-surface-2 border-white/5"
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Project Code (Optional)"
              placeholder="e.g. MET-04"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="bg-surface-2 border-white/5"
            />
            <Input
              label="Estimated Budget (PKR)"
              type="number"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              className="bg-surface-2 border-white/5"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="bg-surface-2 border-white/5"
            />
            <Input
              label="Client Name"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              className="bg-surface-2 border-white/5"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Planned Start Date"
              type="date"
              value={plannedStart}
              onChange={(e) => setPlannedStart(e.target.value)}
              className="bg-surface-2 border-white/5"
            />
            <Input
              label="Planned Finish Date"
              type="date"
              value={plannedFinish}
              onChange={(e) => setPlannedFinish(e.target.value)}
              className="bg-surface-2 border-white/5"
            />
          </div>
          <div className="space-y-1.5 flex flex-col">
            <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Project Description</label>
            <textarea
              placeholder="Provide key metrics (high-rise residential, bridge segment width, structural concrete volumes)..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full h-24 bg-surface-2 border border-white/5 rounded-xl p-3.5 text-xs text-foreground focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-zinc-600"
            />
          </div>

          <div className="pt-4 flex items-center justify-end space-x-3 border-t border-white/5">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setIsModalOpen(false)}
              className="text-zinc-400 hover:text-white rounded-xl h-11"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="rounded-xl h-11 shadow-lg px-6"
            >
              Initialize & Start
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
