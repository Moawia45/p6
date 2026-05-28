/**
 * ConstructMind AI - Backend API Client
 * Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744
 */

import { API_BASE_URL } from './constants';
import { 
  Project, 
  Activity, 
  WBS, 
  Relationship, 
  Resource, 
  ResourceAssignment, 
  BOQItem, 
  GanttData, 
  CPMResult,
  CopilotResponse,
  AIReportResponse
} from '../types/project';

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Set headers
    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    
    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        let errorMsg = `API Error ${response.status}: ${response.statusText}`;
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errorMsg;
        } catch {
          // Response is not JSON
        }
        throw new Error(errorMsg);
      }
      
      return (await response.json()) as T;
    } catch (error) {
      console.error(`Request to ${url} failed:`, error);
      throw error;
    }
  }

  // ── Projects ──────────────────────────────────────────────────
  async getProjects(ownerId?: string): Promise<Project[]> {
    const query = ownerId ? `?owner_id=${encodeURIComponent(ownerId)}` : '';
    return this.request<Project[]>(`/api/projects/${query}`);
  }

  async getProject(id: string): Promise<Project> {
    return this.request<Project>(`/api/projects/${id}`);
  }

  async createProject(data: Partial<Project>): Promise<Project> {
    return this.request<Project>('/api/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: string, data: Partial<Project>): Promise<Project> {
    return this.request<Project>(`/api/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteProject(id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${id}`, {
      method: 'DELETE',
    });
  }

  // ── Activities ───────────────────────────────────────────────
  async getActivities(projectId: string): Promise<Activity[]> {
    return this.request<Activity[]>(`/api/projects/${projectId}/activities/`);
  }

  async createActivity(projectId: string, data: any): Promise<Activity> {
    return this.request<Activity>(`/api/projects/${projectId}/activities/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateActivity(projectId: string, id: string, data: any): Promise<Activity> {
    return this.request<Activity>(`/api/projects/${projectId}/activities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteActivity(projectId: string, id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${projectId}/activities/${id}`, {
      method: 'DELETE',
    });
  }

  async generateActivitiesAI(
    projectId: string, 
    params: { project_description?: string; boq_item_ids?: string[]; project_type: string; detail_level: string }
  ): Promise<{ activities: any[]; relationships: any[]; wbs_suggestions: any[]; ai_notes: string }> {
    return this.request<any>(`/api/projects/${projectId}/activities/generate`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async bulkCreateActivities(projectId: string, activities: any[]): Promise<Activity[]> {
    return this.request<Activity[]>(`/api/projects/${projectId}/activities/bulk`, {
      method: 'POST',
      body: JSON.stringify({ activities }),
    });
  }

  async estimateDurationsAI(
    projectId: string, 
    params: { activity_ids: string[]; mode: string; weather_factor: number; overtime_hours: number; site_constraint_factor: number }
  ): Promise<{ estimations: any[]; mode: string; notes: string }> {
    return this.request<any>(`/api/projects/${projectId}/activities/estimate-durations`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // ── BOQ ──────────────────────────────────────────────────────
  async getBOQItems(projectId: string): Promise<BOQItem[]> {
    return this.request<BOQItem[]>(`/api/projects/${projectId}/boq/`);
  }

  async uploadBOQ(projectId: string, file: File): Promise<{ message: string; items_parsed: number; items_created: number; items: BOQItem[] }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request<any>(`/api/projects/${projectId}/boq/upload`, {
      method: 'POST',
      body: formData,
    });
  }

  async analyzeBOQ(projectId: string): Promise<BOQItem[]> {
    return this.request<BOQItem[]>(`/api/projects/${projectId}/boq/analyze`, {
      method: 'POST',
    });
  }

  async convertBOQ(projectId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${projectId}/boq/convert`, {
      method: 'POST',
    });
  }

  // ── Schedule / CPM ──────────────────────────────────────────
  async getGanttData(projectId: string): Promise<GanttData> {
    return this.request<GanttData>(`/api/projects/${projectId}/schedule/gantt`);
  }

  async calculateCPM(
    projectId: string, 
    params: { project_start: string; calendar_type: string; hours_per_day: number }
  ): Promise<CPMResult> {
    return this.request<CPMResult>(`/api/projects/${projectId}/schedule/cpm`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async createRelationship(projectId: string, data: { predecessor_id: string; successor_id: string; relationship_type: string; lag_days: number }): Promise<Relationship> {
    return this.request<Relationship>(`/api/projects/${projectId}/schedule/relationships`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteRelationship(projectId: string, id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${projectId}/schedule/relationships/${id}`, {
      method: 'DELETE',
    });
  }

  // ── Resources ────────────────────────────────────────────────
  async getResources(projectId: string): Promise<Resource[]> {
    return this.request<Resource[]>(`/api/projects/${projectId}/resources/`);
  }

  async createResource(projectId: string, data: any): Promise<Resource> {
    return this.request<Resource>(`/api/projects/${projectId}/resources/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateResource(projectId: string, id: string, data: any): Promise<Resource> {
    return this.request<Resource>(`/api/projects/${projectId}/resources/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteResource(projectId: string, id: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${projectId}/resources/${id}`, {
      method: 'DELETE',
    });
  }

  async getResourceAssignments(projectId: string): Promise<ResourceAssignment[]> {
    return this.request<ResourceAssignment[]>(`/api/projects/${projectId}/resources/assignments`);
  }

  async assignResource(projectId: string, data: { activity_id: string; resource_id: string; units: number }): Promise<ResourceAssignment> {
    return this.request<ResourceAssignment>(`/api/projects/${projectId}/resources/assignments`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async removeResourceAssignment(projectId: string, assignmentId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/projects/${projectId}/resources/assignments/${assignmentId}`, {
      method: 'DELETE',
    });
  }

  // ── Reports ──────────────────────────────────────────────────
  async generateReport(
    projectId: string, 
    params: { report_type: string; include_charts?: boolean }
  ): Promise<AIReportResponse> {
    return this.request<AIReportResponse>(`/api/projects/${projectId}/reports/generate`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // ── Copilot ──────────────────────────────────────────────────
  async askCopilot(message: string, history: any[], projectId?: string): Promise<CopilotResponse> {
    return this.request<CopilotResponse>('/api/copilot/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_history: history,
        project_id: projectId,
        stream: false,
      }),
    });
  }
}

export const api = new ApiClient();
