import { Card, CardContent } from '@/components/atoms/ui/Card';
import { Input } from '@/components/atoms/ui/Input';
import { StatusFilter } from '@/components/molecules/StatusFilter';
import { DateFilter } from '@/components/molecules/DateFilter';
import { Search } from 'lucide-react';
import type { JobStatus } from '@/types';

type DateFilterType = 'today' | 'this_week' | 'this_month' | null;

interface ApplicationsFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: JobStatus[];
  onStatusChange: (statuses: JobStatus[]) => void;
  dateFilter: DateFilterType;
  onDateFilterChange: (filter: DateFilterType) => void;
  showProgressTracker: boolean;
  onToggleProgressTracker: () => void;
}

/**
 * Applications filters component.
 * Handles search, status filter, date filter, and progress tracker toggle.
 */
export function ApplicationsFilters({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  dateFilter,
  onDateFilterChange,
  showProgressTracker,
  onToggleProgressTracker,
}: ApplicationsFiltersProps) {
  const hasActiveFilters =
    searchQuery.length > 0 || statusFilter.length > 0 || dateFilter !== null;

  const clearAllFilters = () => {
    onSearchChange('');
    onStatusChange([]);
    onDateFilterChange(null);
  };

  return (
    <Card>
      <CardContent className="py-4">
        <div className="space-y-4">
          {/* Top Row: Search, Progress Toggle, Status Filter */}
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search by company or position..."
                  value={searchQuery}
                  onChange={(e) => onSearchChange(e.target.value)}
                  className="pl-10"
                />
              </div>
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
                onClick={onToggleProgressTracker}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${
                  showProgressTracker ? 'bg-primary' : 'bg-muted'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    showProgressTracker ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Status Filter */}
            <StatusFilter
              selectedStatuses={statusFilter}
              onStatusChange={onStatusChange}
              onClear={hasActiveFilters ? clearAllFilters : undefined}
            />
          </div>

          {/* Bottom Row: Date Filters */}
          <DateFilter
            value={dateFilter}
            onChange={onDateFilterChange}
            onClear={hasActiveFilters ? clearAllFilters : undefined}
          />
        </div>
      </CardContent>
    </Card>
  );
}

