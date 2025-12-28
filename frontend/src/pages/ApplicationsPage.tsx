import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { ProgressTracker } from '@/components/ProgressTracker';
import { formatDate } from '@/lib/utils';
import { getValidNextStatuses } from '@/lib/statusTransitions';
import { Link } from 'react-router-dom';
import { Search, Filter, ExternalLink, Mail, Send, MoreVertical } from 'lucide-react';
import { toast } from 'sonner';
import type { Application, JobStatus } from '@/types';

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
  'offer_rejected',
];

export default function ApplicationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const [actionMenuOpen, setActionMenuOpen] = useState<number | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<Record<number, string>>({});
  const [showProgressTracker, setShowProgressTracker] = useState(true);
  const limit = 20;
  const queryClient = useQueryClient();

  // Fetch applications with filters
  const { data, isLoading, error } = useQuery({
    queryKey: ['applications', statusFilter, page],
    queryFn: () =>
      applicationsApi.list({
        status: statusFilter || undefined,
        limit,
        offset: page * limit,
      }),
  });

  // Search query (separate from filter)
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ['applications', 'search', searchQuery],
    queryFn: () => applicationsApi.search(searchQuery),
    enabled: searchQuery.length > 2,
  });

  const applications: Application[] = searchQuery.length > 2
    ? (searchResults?.items as Application[] || [])
    : (data?.items as Application[] || []);

  const total = searchQuery.length > 2 ? searchResults?.total || 0 : data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  const triggerReachOutMutation = useMutation({
    mutationFn: (id: number) => applicationsApi.triggerReachOut(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      toast.success(data.message || 'Reach-out email sent successfully');
      setActionMenuOpen(null);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to send reach-out email');
    },
  });

  const triggerFollowUpMutation = useMutation({
    mutationFn: (id: number) => applicationsApi.triggerFollowUp(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      toast.success(data.message || 'Follow-up email sent successfully');
      setActionMenuOpen(null);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to send follow-up email');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: number; status: string; notes?: string }) =>
      applicationsApi.updateStatus(id, status, notes),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', variables.id] });
      toast.success('Status updated successfully');
      setSelectedStatus({ ...selectedStatus, [variables.id]: '' });
      setActionMenuOpen(null);
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to update status');
    },
  });

  const handleQuickStatusUpdate = (appId: number, status: JobStatus) => {
    updateStatusMutation.mutate({ id: appId, status });
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      // Check if click is on a menu button (MoreVertical icon)
      const isMenuButton = target.closest('button')?.querySelector('svg');
      // Check if click is inside any action menu
      const isInsideMenu = target.closest('[data-action-menu]');

      if (!isMenuButton && !isInsideMenu && actionMenuOpen !== null) {
        setActionMenuOpen(null);
      }
    };

    if (actionMenuOpen !== null) {
      // Use a small delay to avoid closing immediately when opening
      const timeoutId = setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
      }, 0);

      return () => {
        clearTimeout(timeoutId);
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [actionMenuOpen]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Applications</h2>
          <p className="text-muted-foreground">
            Manage and track your job applications
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                placeholder="Search by company or position..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="h-11 pl-10 text-base"
              />
            </div>

            {/* Show Progress Tracker Toggle */}
            <div className="flex items-center gap-2">
              <label htmlFor="progress-toggle" className="text-sm font-medium cursor-pointer">
                Show Progress Tracker
              </label>
              <button
                id="progress-toggle"
                type="button"
                role="switch"
                aria-checked={showProgressTracker}
                onClick={() => setShowProgressTracker(!showProgressTracker)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${showProgressTracker ? 'bg-primary' : 'bg-muted'
                  }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${showProgressTracker ? 'translate-x-6' : 'translate-x-1'
                    }`}
                />
              </button>
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2 md:w-48">
              <Filter className="h-4 w-4 text-muted-foreground flex-shrink-0" />
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(0);
                }}
                className="h-11 flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors"
              >
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Applications Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            {total} Application{total !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading || isSearching ? (
            <div className="py-12">
              <Spinner />
            </div>
          ) : error ? (
            <div className="py-12 text-center text-red-600">
              Error loading applications. Please try again.
            </div>
          ) : applications.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              {searchQuery ? 'No applications found matching your search.' : 'No applications found.'}
            </div>
          ) : (
            <div className="space-y-3">
              {applications.map((app) => (
                <div
                  key={app.id}
                  className="block rounded-xl border p-5 transition-all hover:shadow-md hover:border-primary/50 group relative"
                >
                  <div className="flex items-start justify-between gap-4">
                    <Link to={`/applications/${app.id}`} className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg group-hover:text-primary transition-colors truncate">{app.company_name}</h3>
                        {app.job_posting_url && (
                          <a
                            href={app.job_posting_url.startsWith('http') ? app.job_posting_url : `https://${app.job_posting_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-primary hover:text-primary/80 flex-shrink-0"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                      <p className="text-sm text-foreground/80 truncate">{app.position}</p>
                      {app.location && (
                        <p className="text-xs text-muted-foreground truncate">{app.location}</p>
                      )}
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground pt-1">
                        <span>Created {formatDate(app.created_at)}</span>
                        {app.applied_at && (
                          <span>Applied {formatDate(app.applied_at)}</span>
                        )}
                        {app.emails_count !== undefined && app.emails_count > 0 && (
                          <span className="flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {app.emails_count}
                          </span>
                        )}
                      </div>
                    </Link>
                    <div className="flex flex-col items-end gap-2 flex-shrink-0">
                      <StatusBadge status={app.status} />
                      <div className="relative">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            setActionMenuOpen(actionMenuOpen === app.id ? null : app.id);
                          }}
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {actionMenuOpen === app.id && (
                          <div
                            data-action-menu
                            className="absolute right-0 top-10 z-50 w-56 rounded-md border bg-background shadow-lg"
                          >
                            <div className="p-2 space-y-1">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="w-full justify-start"
                                onClick={(e) => {
                                  e.preventDefault();
                                  triggerReachOutMutation.mutate(app.id);
                                }}
                                disabled={triggerReachOutMutation.isPending}
                              >
                                <Send className="h-4 w-4 mr-2" />
                                Trigger Reach-out
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="w-full justify-start"
                                onClick={(e) => {
                                  e.preventDefault();
                                  triggerFollowUpMutation.mutate(app.id);
                                }}
                                disabled={triggerFollowUpMutation.isPending}
                              >
                                <Mail className="h-4 w-4 mr-2" />
                                Send Follow-up
                              </Button>
                              <div className="border-t my-1" />
                              <div className="px-2 py-1 text-xs font-medium text-muted-foreground">Quick Status:</div>
                              {(() => {
                                const validNextStatuses = getValidNextStatuses(app.status);
                                if (validNextStatuses.length === 0) {
                                  return (
                                    <div className="px-2 py-1 text-xs text-muted-foreground">
                                      No valid transitions (terminal state)
                                    </div>
                                  );
                                }
                                return validNextStatuses.map((status) => (
                                  <Button
                                    key={status}
                                    variant="ghost"
                                    size="sm"
                                    className="w-full justify-start text-xs"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      handleQuickStatusUpdate(app.id, status);
                                    }}
                                    disabled={updateStatusMutation.isPending || app.status === status}
                                  >
                                    {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                  </Button>
                                ));
                              })()}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  {showProgressTracker && (
                    <div className="mt-4 pt-4 border-t">
                      <ProgressTracker
                        currentStatus={app.status}
                        lastMainFlowStatus={app.last_main_flow_status}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {!searchQuery && totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between border-t pt-4">
              <div className="text-sm text-muted-foreground">
                Page {page + 1} of {totalPages} ({total} total)
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

