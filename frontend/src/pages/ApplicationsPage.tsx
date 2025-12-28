import { useState, useEffect, useRef } from 'react';
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDateTime } from '@/lib/utils';
import { getValidNextStatuses } from '@/lib/statusTransitions';
import { Link } from 'react-router-dom';
import { Search, Filter, ExternalLink, Mail, Send, MoreVertical, ArrowUpDown, ArrowUp, ArrowDown, ChevronDown, ChevronRight, X, Calendar, Clock } from 'lucide-react';
import { ProgressTracker } from '@/components/ProgressTracker';
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

type SortField = 'created_at' | 'updated_at' | 'status' | null;
type SortOrder = 'asc' | 'desc';

export default function ApplicationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<JobStatus[]>([]);
  const [statusFilterOpen, setStatusFilterOpen] = useState(false);
  const [dateFilter, setDateFilter] = useState<'today' | 'this_week' | 'this_month' | null>(null);
  const [actionMenuOpen, setActionMenuOpen] = useState<number | null>(null);
  const [showProgressTracker, setShowProgressTracker] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy] = useState<SortField>('updated_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const limit = 20;
  const queryClient = useQueryClient();
  const observerTarget = useRef<HTMLDivElement>(null);
  const statusFilterRef = useRef<HTMLDivElement>(null);

  // Debounce search query (500ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Calculate date range for filters
  const getDateRange = (filter: 'today' | 'this_week' | 'this_month' | null) => {
    if (!filter) return { date_from: undefined, date_to: undefined };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    switch (filter) {
      case 'today': {
        return {
          date_from: today.toISOString(),
          date_to: new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1).toISOString(),
        };
      }
      case 'this_week': {
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay()); // Start of week (Sunday)
        return {
          date_from: weekStart.toISOString(),
          date_to: new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000 - 1).toISOString(),
        };
      }
      case 'this_month': {
        const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
        const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0, 23, 59, 59, 999);
        return {
          date_from: monthStart.toISOString(),
          date_to: monthEnd.toISOString(),
        };
      }
      default:
        return { date_from: undefined, date_to: undefined };
    }
  };

  const dateRange = getDateRange(dateFilter);

  // Fetch applications with filters and sorting using infinite query
  const { data, isLoading, error, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['applications', statusFilter.sort().join(','), sortBy, sortOrder, debouncedSearchQuery, dateFilter],
    queryFn: async ({ pageParam = 0 }) => {
      return applicationsApi.list({
        statuses: statusFilter.length > 0 ? statusFilter : undefined,
        q: debouncedSearchQuery.length > 2 ? debouncedSearchQuery : undefined,
        limit,
        offset: pageParam as number,
        sort_by: sortBy || undefined,
        order: sortOrder,
        ...dateRange,
      });
    },
    getNextPageParam: (lastPage, allPages) => {
      const totalLoaded = allPages.reduce((sum, page) => sum + page.items.length, 0);
      return totalLoaded < lastPage.total ? totalLoaded : undefined;
    },
    initialPageParam: 0,
  });

  // Flatten paginated results
  const applications: Application[] = data?.pages.flatMap(page => page.items) || [];
  const total = data?.pages[0]?.total || 0;

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  const triggerReachOutMutation = useMutation({
    mutationFn: (id: number) => applicationsApi.triggerReachOut(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      toast.success(data.message || 'Reach-out email sent successfully');
      setActionMenuOpen(null);
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to send reach-out email');
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
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to send follow-up email');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: number; status: string; notes?: string }) =>
      applicationsApi.updateStatus(id, status, notes),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', variables.id] });
      toast.success('Status updated successfully');
      setActionMenuOpen(null);
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to update status');
    },
  });

  const handleQuickStatusUpdate = (appId: number, status: JobStatus) => {
    updateStatusMutation.mutate({ id: appId, status });
  };

  const handleSort = (field: SortField) => {
    if (sortBy === field) {
      // Toggle order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with default order
      setSortBy(field);
      setSortOrder(field === 'updated_at' ? 'desc' : 'asc');
    }
  };

  const toggleRow = (appId: number) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(appId)) {
        newSet.delete(appId);
      } else {
        newSet.add(appId);
      }
      return newSet;
    });
  };

  const handleToggleAll = () => {
    if (showProgressTracker) {
      // Collapse all
      setExpandedRows(new Set());
    } else {
      // Expand all
      setExpandedRows(new Set(applications.map(app => app.id)));
    }
    setShowProgressTracker(!showProgressTracker);
  };

  const clearAllFilters = () => {
    setSearchQuery('');
    setDebouncedSearchQuery('');
    setStatusFilter([]);
    setDateFilter(null);
  };

  const toggleStatusFilter = (status: JobStatus) => {
    setStatusFilter(prev => {
      if (prev.includes(status)) {
        return prev.filter(s => s !== status);
      } else {
        return [...prev, status];
      }
    });
  };

  const hasActiveFilters = debouncedSearchQuery.length > 0 || statusFilter.length > 0 || dateFilter !== null;

  const getSortIcon = (field: SortField) => {
    if (sortBy !== field) {
      return <ArrowUpDown className="h-4 w-4 text-muted-foreground" />;
    }
    return sortOrder === 'asc' ? (
      <ArrowUp className="h-4 w-4 text-primary" />
    ) : (
      <ArrowDown className="h-4 w-4 text-primary" />
    );
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const isMenuButton = target.closest(`[data-app-id="${actionMenuOpen}"]`);
      const isInsideMenu = target.closest('[data-action-menu]');

      if (!isMenuButton && !isInsideMenu && actionMenuOpen !== null) {
        setActionMenuOpen(null);
      }
    };

    if (actionMenuOpen !== null) {
      const timeoutId = setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
      }, 0);

      return () => {
        clearTimeout(timeoutId);
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [actionMenuOpen]);

  // Close status filter dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (statusFilterRef.current && !statusFilterRef.current.contains(event.target as Node)) {
        setStatusFilterOpen(false);
      }
    };

    if (statusFilterOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [statusFilterOpen]);

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
          <div className="space-y-4">
            {/* Top Row: Search and Filters */}
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
                  Show Progress
                </label>
                <button
                  id="progress-toggle"
                  type="button"
                  role="switch"
                  aria-checked={showProgressTracker}
                  onClick={handleToggleAll}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${showProgressTracker ? 'bg-primary' : 'bg-muted'
                    }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${showProgressTracker ? 'translate-x-6' : 'translate-x-1'
                      }`}
                  />
                </button>
              </div>

              {/* Status Filter - Multi-select */}
              <div className="relative md:w-48" ref={statusFilterRef}>
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground z-10" />
                <button
                  type="button"
                  onClick={() => setStatusFilterOpen(!statusFilterOpen)}
                  className="h-11 w-full rounded-lg border border-input bg-background pl-10 pr-8 py-2 text-sm text-left ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors flex items-center justify-between"
                >
                  <span className="truncate">
                    {statusFilter.length === 0
                      ? 'All Statuses'
                      : statusFilter.length === 1
                        ? statusFilter[0].replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                        : `${statusFilter.length} Selected`}
                  </span>
                  <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${statusFilterOpen ? 'rotate-180' : ''}`} />
                </button>
                {statusFilterOpen && (
                  <div className="absolute top-full left-0 right-0 mt-1 z-50 rounded-md border bg-background shadow-lg max-h-60 overflow-auto">
                    <div className="p-2 space-y-1">
                      {STATUS_OPTIONS.map((status) => {
                        const isSelected = statusFilter.includes(status);
                        return (
                          <label
                            key={status}
                            className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-muted cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => toggleStatusFilter(status)}
                              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <span className="text-sm flex-1">
                              {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Bottom Row: Quick Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">Quick Filters:</span>
              <Button
                variant={dateFilter === 'today' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setDateFilter(dateFilter === 'today' ? null : 'today')}
                className="h-8"
              >
                <Calendar className="h-3 w-3 mr-1.5" />
                Today
              </Button>
              <Button
                variant={dateFilter === 'this_week' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setDateFilter(dateFilter === 'this_week' ? null : 'this_week')}
                className="h-8"
              >
                <Clock className="h-3 w-3 mr-1.5" />
                This Week
              </Button>
              <Button
                variant={dateFilter === 'this_month' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setDateFilter(dateFilter === 'this_month' ? null : 'this_month')}
                className="h-8"
              >
                <Calendar className="h-3 w-3 mr-1.5" />
                This Month
              </Button>
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearAllFilters}
                  className="h-8 ml-auto"
                >
                  <X className="h-3 w-3 mr-1.5" />
                  Clear All Filters
                </Button>
              )}
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
          {isLoading ? (
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
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold text-sm w-8"></th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">
                      <button
                        onClick={() => handleSort(null)}
                        className="flex items-center gap-2 hover:text-primary transition-colors"
                      >
                        Company / Position
                      </button>
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">
                      <button
                        onClick={() => handleSort('status')}
                        className="flex items-center gap-2 hover:text-primary transition-colors"
                      >
                        Status
                        {getSortIcon('status')}
                      </button>
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">
                      <button
                        onClick={() => handleSort('created_at')}
                        className="flex items-center gap-2 hover:text-primary transition-colors"
                      >
                        Created
                        {getSortIcon('created_at')}
                      </button>
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">
                      <button
                        onClick={() => handleSort('updated_at')}
                        className="flex items-center gap-2 hover:text-primary transition-colors"
                      >
                        Last Updated
                        {getSortIcon('updated_at')}
                      </button>
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Emails</th>
                    <th className="text-right py-3 px-4 font-semibold text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {applications.map((app) => {
                    const isExpanded = expandedRows.has(app.id);
                    return (
                      <>
                        <tr
                          key={app.id}
                          className="border-b hover:bg-muted/50 transition-colors group"
                        >
                          <td className="py-3 px-4">
                            <button
                              onClick={() => toggleRow(app.id)}
                              className="p-1 hover:bg-muted rounded transition-colors"
                              aria-label={isExpanded ? 'Collapse row' : 'Expand row'}
                            >
                              {isExpanded ? (
                                <ChevronDown className="h-4 w-4 text-muted-foreground" />
                              ) : (
                                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                              )}
                            </button>
                          </td>
                          <td className="py-3 px-4">
                            <Link
                              to={`/applications/${app.id}`}
                              className="flex items-center gap-2 group-hover:text-primary transition-colors"
                            >
                              <div className="min-w-0">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold truncate">{app.company_name}</span>
                                  {app.job_posting_url && (
                                    <a
                                      href={app.job_posting_url.startsWith('http') ? app.job_posting_url : `https://${app.job_posting_url}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      onClick={(e) => e.stopPropagation()}
                                      className="text-primary hover:text-primary/80 flex-shrink-0"
                                    >
                                      <ExternalLink className="h-3 w-3" />
                                    </a>
                                  )}
                                </div>
                                <div className="text-sm text-muted-foreground truncate">{app.position}</div>
                                {app.location && (
                                  <div className="text-xs text-muted-foreground truncate">{app.location}</div>
                                )}
                              </div>
                            </Link>
                          </td>
                          <td className="py-3 px-4">
                            <StatusBadge status={app.status} />
                          </td>
                          <td className="py-3 px-4 text-sm text-muted-foreground">
                            {formatDateTime(app.created_at)}
                          </td>
                          <td className="py-3 px-4 text-sm text-muted-foreground">
                            {formatDateTime(app.updated_at)}
                          </td>
                          <td className="py-3 px-4">
                            {app.emails_count !== undefined && app.emails_count > 0 ? (
                              <span className="flex items-center gap-1 text-sm">
                                <Mail className="h-4 w-4" />
                                {app.emails_count}
                              </span>
                            ) : (
                              <span className="text-sm text-muted-foreground">-</span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center justify-end gap-2">
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
                                  data-app-id={app.id}
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
                          </td>
                        </tr>
                        {isExpanded && (
                          <tr key={`${app.id}-expanded`} className="border-b bg-muted/30">
                            <td colSpan={6} className="py-4 px-4">
                              <div className="pl-8">
                                <ProgressTracker
                                  currentStatus={app.status}
                                  lastMainFlowStatus={app.last_main_flow_status}
                                />
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    );
                  })}
                </tbody>
              </table>

              {/* Infinite scroll trigger */}
              <div ref={observerTarget} className="h-10 flex items-center justify-center">
                {isFetchingNextPage && <Spinner size="sm" />}
                {!hasNextPage && applications.length > 0 && (
                  <p className="text-sm text-muted-foreground">No more applications to load</p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
