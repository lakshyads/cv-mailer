export type JobStatus = 
  | 'draft'
  | 'reached_out'
  | 'applied'
  | 'interview_scheduled'
  | 'interview_in_progress'
  | 'result_awaited'
  | 'offer_received'
  | 'rejected'
  | 'ghosted'
  | 'accepted'
  | 'withdrawn'
  | 'offer_rejected';

export type EmailType = 
  | 'cold_email'
  | 'follow_up'
  | 'thank_you'
  | 'other';

export type EmailStatus = 
  | 'draft'
  | 'sent'
  | 'failed'
  | 'bounced';

export interface Application {
  id: number;
  company_name: string;
  position: string;
  status: JobStatus;
  location?: string;
  job_posting_url?: string;
  expected_salary?: string;
  custom_message?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
  applied_at?: string;
  closed_at?: string;
  recruiters?: Recruiter[];
  emails_count?: number;
  last_main_flow_status?: JobStatus;
}

export interface Recruiter {
  id: number;
  name: string;
  email: string;
  applications_count?: number;
  created_at?: string;
  applications?: Application[];
}

export interface EmailRecord {
  id: number;
  job_application_id: number;
  email_type: EmailType;
  subject: string;
  body?: string;
  recipient_email: string;
  recipient_name: string;
  status: EmailStatus;
  is_follow_up: boolean;
  follow_up_number: number;
  sent_at?: string;
  created_at?: string;
}

export interface TimelineEvent {
  id: string;
  type: 'email_sent' | 'status_change' | 'follow_up' | 'first_contact';
  title: string;
  description?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface Statistics {
  total_applications: number;
  total_emails_sent: number;
  follow_ups_sent: number;
  by_status: Record<JobStatus, number>;
  applications_reached_interviews?: number;
  applications_reached_out?: number;
  interview_breakdown?: {
    interview_scheduled: number;
    interview_in_progress: number;
    result_awaited: number;
    offer_received: number;
    accepted: number;
    offer_rejected: number;
    rejected_after_interview: number;
    ghosted_after_interview: number;
    withdrawn_after_interview: number;
  };
  most_applied_companies?: Array<{ company_name: string; count: number }>;
  recent_applications?: Application[];
}

export interface PaginatedResponse<T> {
  total: number;
  limit: number;
  offset: number;
  items: T[];
}

