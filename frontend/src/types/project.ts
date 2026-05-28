/**
 * ConstructMind AI - TypeScript Type Definitions
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

export interface Project {
  id: string;
  name: string;
  description?: string;
  code?: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  planned_start?: string;
  planned_finish?: string;
  actual_start?: string;
  actual_finish?: string;
  data_date?: string;
  budget?: number;
  currency: string;
  calendar_type: '5_day' | '6_day' | '7_day' | 'custom';
  hours_per_day: number;
  location?: string;
  client_name?: string;
  contractor_name?: string;
  owner_id?: string;
  created_at: string;
  updated_at: string;
  activity_count?: number;
  boq_count?: number;
}

export interface WBS {
  id: string;
  project_id: string;
  parent_id?: string;
  code: string;
  name: string;
  description?: string;
  level: number;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Activity {
  id: string;
  project_id: string;
  wbs_id?: string;
  activity_id: string;
  name: string;
  description?: string;
  activity_type: 'task' | 'milestone' | 'summary' | 'level_of_effort' | 'wbs_summary';
  original_duration: number;
  remaining_duration: number;
  actual_duration: number;
  duration_unit: string;
  planned_start?: string;
  planned_finish?: string;
  actual_start?: string;
  actual_finish?: string;
  early_start?: string;
  early_finish?: string;
  late_start?: string;
  late_finish?: string;
  total_float: number;
  free_float: number;
  is_critical: boolean;
  percent_complete: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed' | 'suspended';
  budgeted_cost: number;
  actual_cost: number;
  quantity: number;
  unit?: string;
  productivity_rate_id?: string;
  sort_order: number;
  ai_generated: boolean;
  ai_confidence?: number;
  created_at: string;
  updated_at: string;
}

export interface Relationship {
  id: string;
  project_id: string;
  predecessor_id: string;
  successor_id: string;
  relationship_type: 'FS' | 'SS' | 'FF' | 'SF';
  lag_days: number;
  created_at: string;
}

export interface Resource {
  id: string;
  project_id: string;
  resource_id: string;
  name: string;
  resource_type: 'labor' | 'equipment' | 'material' | 'subcontractor';
  max_units: number;
  unit_of_measure: string;
  standard_rate: number;
  overtime_rate: number;
  cost_per_use: number;
  email?: string;
  phone?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResourceAssignment {
  id: string;
  activity_id: string;
  resource_id: string;
  units: number;
  planned_units: number;
  actual_units: number;
  remaining_units: number;
  planned_cost: number;
  actual_cost: number;
  created_at: string;
}

export interface BOQItem {
  id: string;
  project_id: string;
  item_no: string;
  description: string;
  csi_code?: string;
  csi_category?: string;
  quantity: number;
  unit: string;
  unit_rate: number;
  total_amount: number;
  source_file?: string;
  source_sheet?: string;
  source_row?: number;
  ai_parsed: boolean;
  ai_category?: string;
  ai_confidence?: number;
  ai_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Risk {
  id: string;
  project_id: string;
  risk_id: string;
  title: string;
  description?: string;
  category?: string;
  probability: number;
  impact: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  mitigation_plan?: string;
  contingency_plan?: string;
  owner?: string;
  status: 'identified' | 'mitigated' | 'occurred' | 'closed';
  schedule_impact_days: number;
  cost_impact: number;
  affected_activity_ids?: Record<string, any>;
  ai_generated: boolean;
  ai_recommendations?: string;
  created_at: string;
  updated_at: string;
}

export interface GanttItem {
  id: string;
  activity_id: string;
  name: string;
  start: string;
  end: string;
  duration: number;
  percent_complete: number;
  is_critical: boolean;
  is_milestone: boolean;
  wbs_id?: string;
  wbs_name?: string;
  predecessors: string[];
  total_float: number;
  status: string;
}

export interface GanttData {
  project_id: string;
  project_name: string;
  items: GanttItem[];
  critical_path: string[];
  project_start?: string;
  project_finish?: string;
}

export interface CPMActivityResult {
  activity_id: string;
  activity_db_id: string;
  name: string;
  duration: number;
  early_start?: string;
  early_finish?: string;
  late_start?: string;
  late_finish?: string;
  total_float: number;
  free_float: number;
  is_critical: boolean;
}

export interface CPMResult {
  project_id: string;
  project_start: string;
  project_finish?: string;
  total_duration_days: number;
  critical_path: string[];
  critical_path_duration: number;
  activities: CPMActivityResult[];
  num_critical_activities: number;
  num_total_activities: number;
  has_circular_dependency: boolean;
  warnings: string[];
}

export interface CopilotMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface CopilotResponse {
  message: string;
  model: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface AIReportResponse {
  report_type: string;
  title: string;
  content: string;
  generated_at: string;
  model_used: string;
  sections: Array<{
    title: string;
    content: string;
    charts?: Array<{
      type: string;
      title: string;
      data: any;
    }>;
  }>;
  recommendations: string[];
}
