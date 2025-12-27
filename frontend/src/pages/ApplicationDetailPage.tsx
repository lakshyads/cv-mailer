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
      <div className="flex items-center gap-4">
        <Link to="/applications">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h2 className="text-3xl font-bold tracking-tight">{application.company_name}</h2>
          <p className="text-muted-foreground">{application.position}</p>
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
                      href={application.job_posting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      View Posting
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
              <CardTitle>Email History</CardTitle>
            </CardHeader>
            <CardContent>
              {emails.length === 0 ? (
                <p className="text-center py-8 text-muted-foreground">
                  No emails sent yet.
                </p>
              ) : (
                <div className="space-y-4">
                  {emails.map((email) => (
                    <div key={email.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <p className="font-medium">{email.subject}</p>
                          </div>
                          <div className="mt-2 space-y-1 text-sm text-muted-foreground">
                            <p>
                              To: {email.recipient_name} ({email.recipient_email})
                            </p>
                            <p>Type: {capitalizeFirst(email.email_type.replace('_', ' '))}</p>
                            {email.is_follow_up && (
                              <p>Follow-up #{email.follow_up_number}</p>
                            )}
                            <p>Sent: {formatDateTime(email.sent_at)}</p>
                          </div>
                        </div>
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                            email.status === 'sent'
                              ? 'bg-green-100 text-green-800'
                              : email.status === 'failed'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
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

