import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDate } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Search, Filter, ExternalLink } from 'lucide-react';
import type { Application, JobStatus } from '@/types';

const STATUS_OPTIONS: JobStatus[] = ['draft', 'applied', 'interviewing', 'offer', 'rejected', 'accepted', 'withdrawn'];

export default function ApplicationsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(0);
  const limit = 20;

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
    ? (searchResults?.applications as Application[] || [])
    : (data?.applications as Application[] || []);

  const total = searchQuery.length > 2 ? searchResults?.total || 0 : data?.total || 0;
  const totalPages = Math.ceil(total / limit);

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
                    {status.charAt(0).toUpperCase() + status.slice(1)}
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
                <Link
                  key={app.id}
                  to={`/applications/${app.id}`}
                  className="block rounded-xl border p-5 transition-all hover:shadow-md hover:border-primary/50 group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0 space-y-2">
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
                    </div>
                    <div className="flex-shrink-0">
                      <StatusBadge status={app.status} />
                    </div>
                  </div>
                </Link>
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

