/**
 * ConstructMind AI - Core Constants
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

export const APP_NAME = 'ConstructMind AI';

export const CREATOR_INFO = {
  name: 'Moawia Husnain',
  title: 'Civil Engineer',
  institution: 'UET Taxila',
  phone: '+923266915744',
  email: 'moawia.civil.uet@gmail.com', // placeholder
};

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const NAVIGATION_ITEMS = [
  { name: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { name: 'Projects', href: '/projects', icon: 'FolderKanban' },
  { name: 'Schedule / Gantt', href: '/schedule', icon: 'Calendar' },
  { name: 'Resources', href: '/resources', icon: 'Users' },
  { name: 'BOQ Analysis', href: '/boq', icon: 'FileSpreadsheet' },
  { name: 'Delay Analysis', href: '/analysis', icon: 'ShieldAlert' },
  { name: 'Reports', href: '/reports', icon: 'FileText' },
  { name: 'Cost Controls', href: '/costs', icon: 'DollarSign' },
];

export const PROJECT_STATUSES = {
  planning: { label: 'Planning', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  active: { label: 'Active', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  on_hold: { label: 'On Hold', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  completed: { label: 'Completed', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  cancelled: { label: 'Cancelled', color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
};

export const ACTIVITY_STATUSES = {
  not_started: { label: 'Not Started', color: 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20' },
  in_progress: { label: 'In Progress', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  completed: { label: 'Completed', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  delayed: { label: 'Delayed', color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  suspended: { label: 'Suspended', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
};

export const ACTIVITY_TYPES = {
  task: 'Task',
  milestone: 'Milestone',
  summary: 'Summary Rollup',
  level_of_effort: 'Level of Effort',
  wbs_summary: 'WBS Summary',
};

export const RELATIONSHIP_TYPES = {
  FS: 'Finish-to-Start (FS)',
  SS: 'Start-to-Start (SS)',
  FF: 'Finish-to-Finish (FF)',
  SF: 'Start-to-Finish (SF)',
};

export const RESOURCE_TYPES = {
  labor: { label: 'Labor', icon: 'User' },
  equipment: { label: 'Equipment', icon: 'Hammer' },
  material: { label: 'Material', icon: 'Box' },
  subcontractor: { label: 'Subcontractor', icon: 'Briefcase' },
};

export const RISK_SEVERITIES = {
  low: { label: 'Low', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  medium: { label: 'Medium', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  high: { label: 'High', color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  critical: { label: 'Critical', color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
};

export const CALENDAR_TYPES = [
  { value: '5_day', label: '5-Day Work Week (Mon-Fri, Sat-Sun Off)' },
  { value: '6_day', label: '6-Day Work Week (Mon-Sat, Sun Off)' },
  { value: '7_day', label: '7-Day Continuous (No Days Off)' },
];

export const MOCK_PROJECTS = [
  {
    id: 'proj-1',
    name: 'Metro Line Extension (Segment 4)',
    code: 'MET-EXT-04',
    status: 'active',
    planned_start: '2026-06-01',
    planned_finish: '2027-02-15',
    budget: 45000000,
    currency: 'PKR',
    created_at: '2026-05-10T08:00:00Z',
    progress: 35.5,
    activity_count: 85,
    location: 'Lahore, Pakistan',
    client_name: 'Punjab Mass Transit Authority',
  },
  {
    id: 'proj-2',
    name: 'Goldcrest Residency High-Rise',
    code: 'GCR-HR-02',
    status: 'planning',
    planned_start: '2026-08-01',
    planned_finish: '2028-06-30',
    budget: 185000000,
    currency: 'PKR',
    created_at: '2026-05-15T10:30:00Z',
    progress: 0,
    activity_count: 154,
    location: 'Islamabad, Pakistan',
    client_name: 'Giga Group Developments',
  },
  {
    id: 'proj-3',
    name: 'Industrial Warehouse Complex',
    code: 'IWC-COM-12',
    status: 'on_hold',
    planned_start: '2026-03-01',
    planned_finish: '2026-11-30',
    budget: 32000000,
    currency: 'PKR',
    created_at: '2026-02-01T09:15:00Z',
    progress: 72.0,
    activity_count: 42,
    location: 'Karachi Industrial Zone',
    client_name: 'Al-Khidmat Logistics Ltd',
  }
];
