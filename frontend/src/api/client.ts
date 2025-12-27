import axios from 'axios';
import type { Application, Recruiter, EmailRecord, Statistics, PaginatedResponse } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Applications API
export const applicationsApi = {
  list: async (params?: { status?: string; limit?: number; offset?: number }) => {
    const { data } = await api.get<PaginatedResponse<Application>>('/applications', { params });
    return data;
  },

  search: async (query: string, limit = 50) => {
    const { data } = await api.get<PaginatedResponse<Application>>('/applications/search', {
      params: { q: query, limit },
    });
    return data;
  },

  get: async (id: number) => {
    const { data } = await api.get<Application>(`/applications/${id}`);
    return data;
  },

  updateStatus: async (id: number, status: string, notes?: string) => {
    const { data } = await api.put(`/applications/${id}/status`, null, {
      params: { status, notes },
    });
    return data;
  },

  getEmails: async (id: number) => {
    const { data } = await api.get<{ application_id: number; emails: EmailRecord[] }>(
      `/applications/${id}/emails`
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

export default api;

