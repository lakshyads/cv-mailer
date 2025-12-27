import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { recruitersApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingScreen } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDate } from '@/lib/utils';
import { ArrowLeft, User, Mail, Calendar, Briefcase } from 'lucide-react';

export default function RecruiterDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: recruiter, isLoading } = useQuery({
    queryKey: ['recruiter', id],
    queryFn: () => recruitersApi.get(Number(id)),
    enabled: !!id,
  });

  if (isLoading || !recruiter) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/recruiters">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div className="flex-1">
          <h2 className="text-3xl font-bold tracking-tight">{recruiter.name}</h2>
          <p className="text-muted-foreground">{recruiter.email}</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Recruiter Info */}
        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <User className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Name</p>
                <p className="text-sm text-muted-foreground">{recruiter.name}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Email</p>
                <p className="text-sm text-muted-foreground">{recruiter.email}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Briefcase className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Total Applications</p>
                <p className="text-sm text-muted-foreground">
                  {recruiter.applications?.length || 0}
                </p>
              </div>
            </div>

            {recruiter.created_at && (
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Added</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(recruiter.created_at)}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Applications */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Associated Applications</CardTitle>
            </CardHeader>
            <CardContent>
              {!recruiter.applications || recruiter.applications.length === 0 ? (
                <p className="text-center py-8 text-muted-foreground">
                  No applications associated with this recruiter.
                </p>
              ) : (
                <div className="space-y-4">
                  {recruiter.applications.map((app) => (
                    <Link
                      key={app.id}
                      to={`/applications/${app.id}`}
                      className="block rounded-lg border p-4 transition-colors hover:bg-gray-50"
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <h3 className="font-semibold">{app.company_name}</h3>
                          <p className="text-sm text-muted-foreground">{app.position}</p>
                        </div>
                        <StatusBadge status={app.status} />
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

