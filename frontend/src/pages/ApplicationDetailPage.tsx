import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingScreen, Spinner } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDate, formatDateTime, capitalizeFirst } from '@/lib/utils';
import { ArrowLeft, ExternalLink, Mail, User, Calendar, MapPin, DollarSign, FileText } from 'lucide-react';
import { toast } from 'sonner';
import type { JobStatus } from '@/types';

const STATUS_OPTIONS: JobStatus[] = ['draft', 'applied', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn'];

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [notes, setNotes] = useState('');

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
    onError: () => {
      toast.error('Failed to update status');
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
          <h2 className="text-3xl font-bold tracking-tight">{application.company_name}</h2>
          <p className="text-lg text-muted-foreground mt-1">{application.position}</p>
        </div>
        <StatusBadge status={application.status} />
      </div>

      {/* Main Info */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          {/* Details Card */}
          <Card>
            <CardHeader>
              <CardTitle>Application Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {application.location && (
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">{application.location}</p>
                  </div>
                </div>
              )}

              {application.expected_salary && (
                <div className="flex items-start gap-3">
                  <DollarSign className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Expected Salary</p>
                    <p className="text-sm text-muted-foreground">{application.expected_salary}</p>
                  </div>
                </div>
              )}

              {application.job_posting_url && (
                <div className="flex items-start gap-3">
                  <ExternalLink className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Job Posting</p>
                    <a
                      href={application.job_posting_url.startsWith('http') ? application.job_posting_url : `https://${application.job_posting_url}`}
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
                    <p>Created: {formatDate(application.created_at)}</p>
                    {application.applied_at && <p>Applied: {formatDate(application.applied_at)}</p>}
                    {application.updated_at && <p>Last Updated: {formatDate(application.updated_at)}</p>}
                    {application.closed_at && <p>Closed: {formatDate(application.closed_at)}</p>}
                  </div>
                </div>
              </div>

              {application.custom_message && (
                <div className="flex items-start gap-3">
                  <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Custom Message</p>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {application.custom_message}
                    </p>
                  </div>
                </div>
              )}

              {application.notes && (
                <div className="flex items-start gap-3">
                  <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Notes</p>
                    <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {application.notes}
                    </p>
                  </div>
                </div>
              )}
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
                  <p className="text-sm mt-1">Use CLI to send emails to this application.</p>
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
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold flex-shrink-0 ${
                            email.status === 'sent'
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
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Recruiters */}
          <Card>
            <CardHeader>
              <CardTitle>Recruiters</CardTitle>
            </CardHeader>
            <CardContent>
              {application.recruiters && application.recruiters.length > 0 ? (
                <div className="space-y-3">
                  {application.recruiters.map((recruiter) => (
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

          {/* Update Status */}
          <Card>
            <CardHeader>
              <CardTitle>Update Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">New Status</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select status...</option>
                  {STATUS_OPTIONS.map((status) => (
                    <option key={status} value={status}>
                      {capitalizeFirst(status)}
                    </option>
                  ))}
                </select>
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
    </div>
  );
}

