import axios from 'axios';
import type { Application, Recruiter, EmailRecord, Statistics, PaginatedResponse, TimelineEvent, ConversationListResponse, ConversationThread } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Applications API
export const applicationsApi = {
  list: async (params?: { 
    status?: string; // Deprecated, use statuses
    statuses?: string[]; // Array of statuses for multi-select
    q?: string; // Search query
    date_from?: string; // ISO date string
    date_to?: string; // ISO date string
    limit?: number; 
    offset?: number;
    sort_by?: 'created_at' | 'updated_at' | 'status';
    order?: 'asc' | 'desc';
  }) => {
    // Build params manually to ensure arrays are sent correctly for FastAPI
    const queryParams: Record<string, string | number | string[]> = {};
    
    if (params?.statuses && params.statuses.length > 0) {
      // FastAPI expects multiple query params with same name: ?statuses=value1&statuses=value2
      queryParams.statuses = params.statuses;
    }
    if (params?.status) {
      queryParams.status = params.status;
    }
    if (params?.q) {
      queryParams.q = params.q;
    }
    if (params?.date_from) {
      queryParams.date_from = params.date_from;
    }
    if (params?.date_to) {
      queryParams.date_to = params.date_to;
    }
    if (params?.limit !== undefined) {
      queryParams.limit = params.limit;
    }
    if (params?.offset !== undefined) {
      queryParams.offset = params.offset;
    }
    if (params?.sort_by) {
      queryParams.sort_by = params.sort_by;
    }
    if (params?.order) {
      queryParams.order = params.order;
    }

    const { data } = await api.get<PaginatedResponse<Application>>('/applications', { 
      params: queryParams,
      paramsSerializer: (params) => {
        // Custom serializer to handle arrays correctly for FastAPI
        const parts: string[] = [];
        for (const [key, value] of Object.entries(params)) {
          if (Array.isArray(value)) {
            // FastAPI expects: statuses=value1&statuses=value2 (no brackets)
            value.forEach(v => parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`));
          } else if (value !== undefined && value !== null) {
            parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
          }
        }
        return parts.join('&');
      }
    });
    return data;
  },

  get: async (id: number) => {
    const { data } = await api.get<Application>(`/applications/${id}`);
    return data;
  },

  updateStatus: async (id: number, status: string, notes?: string) => {
    const { data } = await api.put(`/applications/${id}/status`, {
      status,
      notes,
    });
    return data;
  },

  getEmails: async (id: number) => {
    const { data } = await api.get<{ application_id: number; emails: EmailRecord[] }>(
      `/applications/${id}/emails`
    );
    return data;
  },

  triggerReachOut: async (id: number, recruiterId?: number) => {
    const { data } = await api.post<{ message: string; sent_count: number; failed_count: number }>(
      `/applications/${id}/trigger-reach-out`,
      null,
      { params: recruiterId ? { recruiter_id: recruiterId } : {} }
    );
    return data;
  },

  triggerFollowUp: async (id: number, recruiterId?: number, recruiterIds?: number[]) => {
    const params: Record<string, number | number[]> = {};
    if (recruiterIds && recruiterIds.length > 0) {
      // Use new recruiter_ids array
      params.recruiter_ids = recruiterIds;
    } else if (recruiterId) {
      // Fallback to single recruiter_id for backward compatibility
      params.recruiter_id = recruiterId;
    }
    
    const { data } = await api.post<{ message: string; sent_count: number; failed_count: number }>(
      `/applications/${id}/trigger-follow-up`,
      null,
      { 
        params,
        paramsSerializer: (params) => {
          const parts: string[] = [];
          for (const [key, value] of Object.entries(params)) {
            if (Array.isArray(value)) {
              value.forEach(v => parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(v)}`));
            } else if (value !== undefined && value !== null) {
              parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
            }
          }
          return parts.join('&');
        }
      }
    );
    return data;
  },

  getConversations: async (id: number) => {
    const { data } = await api.get<ConversationListResponse>(
      `/applications/${id}/conversations`
    );
    return data;
  },

  getRecruiterConversation: async (id: number, recruiterId: number) => {
    const { data } = await api.get<ConversationThread>(
      `/applications/${id}/conversations/${recruiterId}`
    );
    return data;
  },

  getTimeline: async (id: number) => {
    const { data } = await api.get<{ application_id: number; events: TimelineEvent[] }>(
      `/applications/${id}/timeline`
    );
    return data;
  },
};

// Emails API
export const emailsApi = {
  list: async (params?: { status?: string; limit?: number; offset?: number }) => {
    const { data } = await api.get<PaginatedResponse<EmailRecord>>('/emails', { params });
    return data;
  },
};

// Recruiters API
export const recruitersApi = {
  list: async (params?: { limit?: number; offset?: number }) => {
    const { data } = await api.get<PaginatedResponse<Recruiter>>('/recruiters', { params });
    return data;
  },

  get: async (id: number) => {
    const { data } = await api.get<Recruiter>(`/recruiters/${id}`);
    return data;
  },
};

// Statistics API
export const statisticsApi = {
  get: async () => {
    const { data } = await api.get<Statistics>('/statistics');
    return data;
  },

  getSummary: async () => {
    const { data } = await api.get<Statistics>('/statistics/summary');
    return data;
  },
};

// Sync API
export const syncApi = {
  syncApplications: async (dryRun: boolean = false) => {
    const { data } = await api.post<{
      sent_count: number;
      skipped_count: number;
      total_rows: number;
      errors?: string[];
      message: string;
    }>('/sync/applications', null, {
      params: { dry_run: dryRun },
    });
    return data;
  },

  sendFollowUps: async (dryRun: boolean = false) => {
    const { data } = await api.post<{
      sent_count: number;
      skipped_count: number;
      total_needing: number;
      errors?: string[];
      message: string;
    }>('/sync/follow-ups', null, {
      params: { dry_run: dryRun },
    });
    return data;
  },
};

export default api;

