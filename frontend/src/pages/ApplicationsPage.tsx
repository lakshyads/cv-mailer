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
          <div className="flex flex-col gap-4 md:flex-row">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by company or position..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(0);
                }}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
            <div className="space-y-4">
              {applications.map((app) => (
                <Link
                  key={app.id}
                  to={`/applications/${app.id}`}
                  className="block rounded-lg border p-4 transition-colors hover:bg-gray-50"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-lg">{app.company_name}</h3>
                        {app.job_posting_url && (
                          <a
                            href={app.job_posting_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-blue-600 hover:text-blue-700"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{app.position}</p>
                      {app.location && (
                        <p className="text-xs text-muted-foreground">{app.location}</p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2">
                        <span>Created: {formatDate(app.created_at)}</span>
                        {app.applied_at && (
                          <span>Applied: {formatDate(app.applied_at)}</span>
                        )}
                        {app.emails_count !== undefined && (
                          <span>{app.emails_count} email{app.emails_count !== 1 ? 's' : ''}</span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4">
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

