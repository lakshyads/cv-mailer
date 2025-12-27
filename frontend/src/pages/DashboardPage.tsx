import { useQuery } from '@tanstack/react-query';
import { statisticsApi, applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingScreen } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDate, capitalizeFirst } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Briefcase, Mail, TrendingUp, Clock, ArrowUpRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const STATUS_COLORS: Record<string, string> = {
  draft: '#94a3b8',
  applied: '#3b82f6',
  interviewing: '#8b5cf6',
  offer: '#10b981',
  rejected: '#ef4444',
  accepted: '#059669',
  withdrawn: '#f59e0b',
};

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => statisticsApi.get(),
  });

  const { data: recentApps } = useQuery({
    queryKey: ['applications', 'recent'],
    queryFn: () => applicationsApi.list({ limit: 5 }),
  });

  if (isLoading || !stats) {
    return <LoadingScreen />;
  }

  // Prepare data for charts
  const statusBarData = Object.entries(stats.by_status).map(([status, count]) => ({
    status: capitalizeFirst(status),
    statusKey: status,
    count,
  }));

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Total Applications</p>
                <p className="text-3xl font-bold">{stats.total_applications}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Briefcase className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Emails Sent</p>
                <p className="text-3xl font-bold">{stats.total_emails_sent}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                <Mail className="h-6 w-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Follow-ups</p>
                <p className="text-3xl font-bold">{stats.follow_ups_sent}</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-purple-500/10 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-purple-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Response Rate</p>
                <p className="text-3xl font-bold">
                  {stats.total_applications > 0
                    ? Math.round(((stats.by_status.interviewing || 0) / stats.total_applications) * 100)
                    : 0}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <Clock className="h-6 w-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Application Status Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Application Status Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusBarData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
                <XAxis
                  dataKey="status"
                  className="text-xs"
                  tick={{ fill: 'currentColor', className: 'fill-muted-foreground' }}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: 'currentColor', className: 'fill-muted-foreground' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {statusBarData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.statusKey] || '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {statusBarData
                .sort((a, b) => b.count - a.count)
                .map((item) => (
                  <div key={item.statusKey} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="h-3 w-3 rounded-full"
                        style={{ backgroundColor: STATUS_COLORS[item.statusKey] }}
                      />
                      <span className="text-sm font-medium">{item.status}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{item.count}</span>
                      <span className="text-xs text-muted-foreground">
                        ({Math.round((item.count / stats.total_applications) * 100)}%)
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Applications */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Applications</CardTitle>
            <Link
              to="/applications"
              className="text-sm font-medium text-primary hover:underline flex items-center gap-1"
            >
              View all
              <ArrowUpRight className="h-4 w-4" />
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {recentApps?.applications?.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No applications yet.</p>
              <p className="text-sm mt-1">Start by syncing from Google Sheets!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentApps?.applications?.map((app) => (
                <Link
                  key={app.id}
                  to={`/applications/${app.id}`}
                  className="flex items-center justify-between rounded-xl border p-4 transition-all hover:shadow-md hover:border-primary/50 group"
                >
                  <div className="flex-1 space-y-1">
                    <p className="font-semibold group-hover:text-primary transition-colors">{app.company_name}</p>
                    <p className="text-sm text-muted-foreground">{app.position}</p>
                    {app.location && (
                      <p className="text-xs text-muted-foreground">{app.location}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">
                        {formatDate(app.created_at)}
                      </p>
                      {app.emails_count !== undefined && app.emails_count > 0 && (
                        <p className="text-xs text-muted-foreground flex items-center justify-end gap-1 mt-1">
                          <Mail className="h-3 w-3" />
                          {app.emails_count}
                        </p>
                      )}
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
  );
}

