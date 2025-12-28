import { useState, useEffect, useRef } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { GoogleSheetsSync } from '@/components/GoogleSheetsSync';
import { ApplicationsFilters } from '@/components/applications/ApplicationsFilters';
import { ApplicationsTable } from '@/components/applications/ApplicationsTable';
import { Spinner } from '@/components/ui/Spinner';
import { getValidNextStatuses } from '@/lib/statusTransitions';
import { useApplicationMutations } from '@/hooks/useApplicationMutations';
import type { Application, JobStatus } from '@/types';

type SortField = 'created_at' | 'updated_at' | 'status' | null;
type SortOrder = 'asc' | 'desc';
type DateFilterType = 'today' | 'this_week' | 'this_month' | null;

export default function ApplicationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<JobStatus[]>([]);
  const [dateFilter, setDateFilter] = useState<DateFilterType>(null);
  const [actionMenuOpen, setActionMenuOpen] = useState<number | null>(null);
  const [showProgressTracker, setShowProgressTracker] = useState(false);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy] = useState<SortField>('updated_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const limit = 20;
  const observerTarget = useRef<HTMLDivElement>(null);

  const { triggerReachOut, triggerFollowUp, updateStatus } = useApplicationMutations();

  // Debounce search query (500ms delay)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Calculate date range for filters
  const getDateRange = (filter: DateFilterType) => {
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
        const monthEnd = new Date(
          today.getFullYear(),
          today.getMonth() + 1,
          0,
          23,
          59,
          59,
          999
        );
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
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: [
      'applications',
      statusFilter.sort().join(','),
      sortBy,
      sortOrder,
      debouncedSearchQuery,
      dateFilter,
    ],
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
  const applications: Application[] = data?.pages.flatMap((page) => page.items) || [];
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
    setExpandedRows((prev) => {
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
      setExpandedRows(new Set(applications.map((app) => app.id)));
    }
    setShowProgressTracker(!showProgressTracker);
  };

  const handleTriggerReachOut = (id: number) => {
    triggerReachOut.mutate(id, {
      onSuccess: () => setActionMenuOpen(null),
    });
  };

  const handleTriggerFollowUp = (id: number) => {
    triggerFollowUp.mutate(id, {
      onSuccess: () => setActionMenuOpen(null),
    });
  };

  const handleUpdateStatus = (id: number, status: string) => {
    updateStatus.mutate(
      { id, status },
      {
        onSuccess: () => setActionMenuOpen(null),
      }
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Applications</h2>
          <p className="text-muted-foreground">Manage and track your job applications</p>
        </div>
      </div>

      {/* Sync Controls */}
      <GoogleSheetsSync />

      {/* Filters */}
      <ApplicationsFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
        dateFilter={dateFilter}
        onDateFilterChange={setDateFilter}
        showProgressTracker={showProgressTracker}
        onToggleProgressTracker={handleToggleAll}
      />

      {/* Applications Table */}
      <ApplicationsTable
        applications={applications}
        total={total}
        isLoading={isLoading}
        error={error as Error | null}
        searchQuery={searchQuery}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
        expandedRows={expandedRows}
        onToggleRow={toggleRow}
        showProgressTracker={showProgressTracker}
        actionMenuOpen={actionMenuOpen}
        onActionMenuToggle={setActionMenuOpen}
        onTriggerReachOut={handleTriggerReachOut}
        onTriggerFollowUp={handleTriggerFollowUp}
        onUpdateStatus={handleUpdateStatus}
        isTriggeringReachOut={(_id) => triggerReachOut.isPending}
        isTriggeringFollowUp={(_id) => triggerFollowUp.isPending}
        isUpdatingStatus={(_id) => updateStatus.isPending}
        getValidNextStatuses={getValidNextStatuses}
      />

      {/* Infinite scroll trigger */}
      <div ref={observerTarget} className="h-10 flex items-center justify-center">
        {isFetchingNextPage && <Spinner size="sm" />}
        {!hasNextPage && applications.length > 0 && (
          <p className="text-sm text-muted-foreground">No more applications to load</p>
        )}
      </div>
    </div>
  );
}
