import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingScreen, Spinner } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { ProgressTracker } from '@/components/ProgressTracker';
import { Timeline } from '@/components/Timeline';
import { formatDate, formatDateTime, capitalizeFirst } from '@/lib/utils';
import { getValidNextStatuses } from '@/lib/statusTransitions';
import { ArrowLeft, ExternalLink, Mail, User, Calendar, MapPin, DollarSign, FileText, X, Eye, Send } from 'lucide-react';
import { toast } from 'sonner';
import type { JobStatus, EmailRecord } from '@/types';

const STATUS_OPTIONS: JobStatus[] = [
  'draft',
  'reached_out',
  'applied',
  'interview_scheduled',
  'interview_in_progress',
  'result_awaited',
  'offer_received',
  'rejected',
  'ghosted',
  'accepted',
  'withdrawn',
];

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [viewingEmail, setViewingEmail] = useState<EmailRecord | null>(null);

  const { data: application, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: () => applicationsApi.get(Number(id)),
    enabled: !!id,
  });

  const { data: emailsData } = useQuery({
    queryKey: ['application', id, 'emails'],
    queryFn: () => applicationsApi.getEmails(Number(id)),
    enabled: !!id,
  });

  const { data: timelineData } = useQuery({
    queryKey: ['application', id, 'timeline'],
    queryFn: () => applicationsApi.getTimeline(Number(id)),
    enabled: !!id,
  });

  const triggerReachOutMutation = useMutation({
    mutationFn: () => applicationsApi.triggerReachOut(Number(id)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'timeline'] });
      toast.success(data.message || 'Reach-out email sent successfully');
    },
    onError: (error: unknown) => {
      const message = error && typeof error === 'object' && 'response' in error
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined;
      toast.error(message || 'Failed to send reach-out email');
    },
  });

  const triggerFollowUpMutation = useMutation({
    mutationFn: () => applicationsApi.triggerFollowUp(Number(id)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'timeline'] });
      toast.success(data.message || 'Follow-up email sent successfully');
    },
    onError: (error: unknown) => {
      const message = error && typeof error === 'object' && 'response' in error
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined;
      toast.error(message || 'Failed to send follow-up email');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ status, notes }: { status: string; notes?: string }) =>
      applicationsApi.updateStatus(Number(id), status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success('Status updated successfully');
      setSelectedStatus('');
      setNotes('');
    },
    onError: (error: any) => {
      // Show the actual error message from the API
      const errorMessage = error?.response?.data?.detail || 'Failed to update status';
      toast.error(errorMessage);
    },
  });

  if (isLoading || !application) {
    return <LoadingScreen />;
  }

  const emails = emailsData?.emails || [];

  const handleUpdateStatus = () => {
    if (!selectedStatus) {
      toast.error('Please select a status');
      return;
    }
    updateStatusMutation.mutate({ status: selectedStatus, notes: notes || undefined });
  };

  // TypeScript: application is guaranteed to be defined here due to early return above
  const app = application;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-start gap-4">
        <Link to="/applications">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1 min-w-0">
          <h2 className="text-3xl font-bold tracking-tight">{app.company_name}</h2>
          <p className="text-lg text-muted-foreground mt-1">{app.position}</p>
        </div>
        <StatusBadge status={app.status} />
      </div>

      {/* Progress Tracker */}
      <Card>
        <CardContent className="pt-6">
          <ProgressTracker currentStatus={app.status} />
        </CardContent>
      </Card>

      {/* Main Info */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          {/* Details Card */}
          <Card>
            <CardHeader>
              <CardTitle>Application Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {app.location && (
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">{app.location}</p>
                  </div>
                </div>
              )}

              {app.expected_salary && (
                <div className="flex items-start gap-3">
                  <DollarSign className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Expected Salary</p>
                    <p className="text-sm text-muted-foreground">{app.expected_salary}</p>
                  </div>
                </div>
              )}

              {app.job_posting_url && (
                <div className="flex items-start gap-3">
                  <ExternalLink className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Job Posting</p>
                    <a
                      href={app.job_posting_url.startsWith('http') ? app.job_posting_url : `https://${app.job_posting_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline flex items-center gap-1"
                    >
                      View Posting
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Timeline</p>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Created: {formatDate(app.created_at)}</p>
                    {app.applied_at && <p>Applied: {formatDate(app.applied_at)}</p>}
                    {app.updated_at && <p>Last Updated: {formatDate(app.updated_at)}</p>}
                    {app.closed_at && <p>Closed: {formatDate(app.closed_at)}</p>}
                  </div>
                </div>
              </div>

              {app.custom_message && (
                <div className="flex items-start gap-3">
                  <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Custom Message</p>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {app.custom_message}
                    </p>
                  </div>
                </div>
              )}

              {app.notes && (
                <div className="flex items-start gap-3">
                  <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Notes</p>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {app.notes}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Timeline and Email History - Side by Side */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <Timeline events={timelineData?.events || []} />
              </CardContent>
            </Card>

            {/* Email History */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Email History</CardTitle>
                  <span className="text-sm text-muted-foreground">{emails.length} email{emails.length !== 1 ? 's' : ''}</span>
                </div>
              </CardHeader>
              <CardContent>
                {emails.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No emails sent yet.</p>
                    <div className="mt-4 flex gap-2 justify-center">
                      <Button
                        size="sm"
                        onClick={() => triggerReachOutMutation.mutate()}
                        disabled={triggerReachOutMutation.isPending}
                      >
                        {triggerReachOutMutation.isPending ? (
                          <>
                            <Spinner size="sm" className="mr-2" />
                            Sending...
                          </>
                        ) : (
                          <>
                            <Send className="h-4 w-4 mr-2" />
                            Send First Contact
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {emails.map((email) => (
                      <div key={email.id} className="border rounded-xl p-4 hover:shadow-sm transition-shadow">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start gap-2 mb-2">
                              <Mail className="h-4 w-4 text-muted-foreground mt-1 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <p className="font-semibold truncate">{email.subject}</p>
                                <p className="text-sm text-muted-foreground mt-1">
                                  To: {email.recipient_name}
                                  <span className="text-xs ml-1">({email.recipient_email})</span>
                                </p>
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground ml-6">
                              <span>{capitalizeFirst(email.email_type.replace('_', ' '))}</span>
                              {email.is_follow_up && (
                                <span className="text-primary font-medium">Follow-up #{email.follow_up_number}</span>
                              )}
                              <span>{formatDateTime(email.sent_at)}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {email.body && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setViewingEmail(email)}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            )}
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${email.status === 'sent'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                : email.status === 'failed'
                                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                  : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                                }`}
                            >
                              {capitalizeFirst(email.status)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Recruiters */}
          <Card>
            <CardHeader>
              <CardTitle>Recruiters</CardTitle>
            </CardHeader>
            <CardContent>
              {app.recruiters && app.recruiters.length > 0 ? (
                <div className="space-y-3">
                  {app.recruiters.map((recruiter) => (
                    <Link
                      key={recruiter.id}
                      to={`/recruiters/${recruiter.id}`}
                      className="flex items-start gap-3 rounded-lg border p-3 hover:bg-gray-50 transition-colors"
                    >
                      <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm">{recruiter.name}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {recruiter.email}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No recruiters assigned</p>
              )}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={() => triggerReachOutMutation.mutate()}
                disabled={triggerReachOutMutation.isPending}
                className="w-full"
                variant="outline"
              >
                {triggerReachOutMutation.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Trigger Reach-out
                  </>
                )}
              </Button>

              <Button
                onClick={() => triggerFollowUpMutation.mutate()}
                disabled={triggerFollowUpMutation.isPending}
                className="w-full"
                variant="outline"
              >
                {triggerFollowUpMutation.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Follow-up
                  </>
                )}
              </Button>

              <div className="border-t pt-4">
                <label className="text-sm font-medium">Update Status</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  disabled={updateStatusMutation.isPending}
                >
                  <option value="">Select status...</option>
                  {application && (() => {
                    const validNextStatuses = getValidNextStatuses(application.status);
                    if (validNextStatuses.length === 0) {
                      return (
                        <option value="" disabled>
                          No valid status transitions (terminal state)
                        </option>
                      );
                    }
                    return validNextStatuses.map((status) => (
                      <option key={status} value={status}>
                        {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </option>
                    ));
                  })()}
                </select>
                {application && getValidNextStatuses(application.status).length === 0 && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    This application is in a terminal state and cannot be changed.
                  </p>
                )}
              </div>

              <div>
                <label className="text-sm font-medium">Notes (optional)</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any notes..."
                  rows={3}
                  className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                />
              </div>

              <Button
                onClick={handleUpdateStatus}
                disabled={!selectedStatus || updateStatusMutation.isPending}
                className="w-full"
              >
                {updateStatusMutation.isPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Updating...
                  </>
                ) : (
                  'Update Status'
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Email Content Modal */}
      {viewingEmail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            <CardHeader className="flex-shrink-0">
              <div className="flex items-center justify-between">
                <CardTitle>{viewingEmail?.subject || ''}</CardTitle>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setViewingEmail(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="text-sm text-muted-foreground mt-2">
                <p>To: {viewingEmail?.recipient_name || ''} ({viewingEmail?.recipient_email || ''})</p>
                <p>Sent: {viewingEmail?.sent_at ? formatDateTime(viewingEmail.sent_at) : 'N/A'}</p>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto">
              {viewingEmail?.body && (
                <div
                  className="prose prose-sm max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: viewingEmail.body }}
                />
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

