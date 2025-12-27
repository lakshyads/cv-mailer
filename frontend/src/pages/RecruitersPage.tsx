import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { recruitersApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Spinner } from '@/components/ui/Spinner';
import { Link } from 'react-router-dom';
import { User, Mail, Briefcase } from 'lucide-react';
import type { Recruiter } from '@/types';

export default function RecruitersPage() {
  const [page, setPage] = useState(0);
  const limit = 50;

  const { data, isLoading, error } = useQuery({
    queryKey: ['recruiters', page],
    queryFn: () => recruitersApi.list({ limit, offset: page * limit }),
  });

  const recruiters = (data?.recruiters as Recruiter[]) || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Recruiters</h2>
        <p className="text-muted-foreground">
          View and manage recruiter contacts
        </p>
      </div>

      {/* Recruiters Grid */}
      <Card>
        <CardHeader>
          <CardTitle>
            {total} Recruiter{total !== 1 ? 's' : ''}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12">
              <Spinner />
            </div>
          ) : error ? (
            <div className="py-12 text-center text-red-600">
              Error loading recruiters. Please try again.
            </div>
          ) : recruiters.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              No recruiters found.
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {recruiters.map((recruiter) => (
                <Link
                  key={recruiter.id}
                  to={`/recruiters/${recruiter.id}`}
                  className="block rounded-xl border p-5 transition-all hover:shadow-md hover:border-primary/50 group"
                >
                  <div className="flex items-start gap-4">
                    <div className="rounded-full bg-gradient-to-br from-primary to-purple-600 p-3 shadow-lg">
                      <User className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0 space-y-2">
                      <h3 className="font-bold group-hover:text-primary transition-colors truncate">{recruiter.name}</h3>
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Mail className="h-3.5 w-3.5 flex-shrink-0" />
                        <span className="truncate">{recruiter.email}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs font-medium text-primary">
                        <Briefcase className="h-3.5 w-3.5 flex-shrink-0" />
                        <span>
                          {recruiter.applications_count || 0} application
                          {recruiter.applications_count !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
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

