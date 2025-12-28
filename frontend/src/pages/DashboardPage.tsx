import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { statisticsApi, applicationsApi, syncApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingScreen } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { formatDateTime, capitalizeFirst } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Briefcase, Mail, TrendingUp, Clock, ArrowUpRight, Info, RefreshCw, Send, Eye } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { toast } from 'sonner';

// Status colors matching our flow
const STATUS_COLORS: Record<string, string> = {
  applied: '#3b82f6',              // Blue - initial state
  reached_out: '#6366f1',          // Indigo - after emails sent
  interview_scheduled: '#8b5cf6',   // Purple - interview scheduled
  interview_in_progress: '#a855f7', // Purple - interview in progress
  result_awaited: '#c084fc',       // Purple - waiting for result
  offer_received: '#10b981',        // Green - offer received
  accepted: '#059669',              // Green - accepted (terminal positive)
  rejected: '#ef4444',              // Red - rejected (terminal negative)
  ghosted: '#f87171',               // Red - ghosted (terminal negative)
  withdrawn: '#f59e0b',             // Orange - withdrawn (terminal negative)
  offer_rejected: '#f59e0b',        // Orange - offer rejected (terminal negative)
  draft: '#94a3b8',                 // Gray - legacy
};

// Status order is now defined inline in the component for better organization

export default function DashboardPage() {
  const [showInterviewTooltip, setShowInterviewTooltip] = useState(false);
  const queryClient = useQueryClient();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => statisticsApi.get(),
  });

  const { data: recentApps } = useQuery({
    queryKey: ['applications', 'recent'],
    queryFn: () => applicationsApi.list({
      limit: 5,
      sort_by: 'updated_at',
      order: 'desc'
    }),
  });

  // Sync mutations
  const syncApplicationsMutation = useMutation({
    mutationFn: (dryRun: boolean) => syncApi.syncApplications(dryRun),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success(data.message || 'Applications synced successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to sync applications');
    },
  });

  const sendFollowUpsMutation = useMutation({
    mutationFn: (dryRun: boolean) => syncApi.sendFollowUps(dryRun),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success(data.message || 'Follow-ups sent successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || 'Failed to send follow-ups');
    },
  });

  if (isLoading || !stats) {
    return <LoadingScreen />;
  }

  // Prepare data for charts - ordered by logical flow
  // Initial stages
  const initialStatuses = ['applied', 'reached_out'];
  // Interview process statuses
  const interviewStatuses = ['interview_scheduled', 'interview_in_progress', 'result_awaited'];
  // Offer stage
  const offerStatuses = ['offer_received'];
  // Terminal states after offer (only show if count > 0)
  const afterOfferStatuses = ['accepted', 'offer_rejected'];
  // Terminal states that can happen earlier (only show if count > 0)
  const earlyTerminalStatuses = ['rejected', 'ghosted', 'withdrawn'];

  // All main flow statuses
  const mainFlowStatuses = [...initialStatuses, ...interviewStatuses, ...offerStatuses];

  // Chart data in logical order: initial → interview → offer → after offer → early termination
  const chartOrder = [...initialStatuses, ...interviewStatuses, ...offerStatuses, ...afterOfferStatuses, ...earlyTerminalStatuses];

  const statusBarData = chartOrder.map((statusKey) => ({
    status: capitalizeFirst(statusKey.replace(/_/g, ' ')),
    statusKey,
    count: (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0,
  })).filter((item) => {
    // Always show main flow statuses, only show terminal if count > 0
    return mainFlowStatuses.includes(item.statusKey) ||
      (afterOfferStatuses.includes(item.statusKey) && item.count > 0) ||
      (earlyTerminalStatuses.includes(item.statusKey) && item.count > 0);
  });

  // Calculate max count for Y-axis domain to reduce white space
  const maxCount = Math.max(...statusBarData.map(item => item.count), 1);
  const yAxisDomain = [0, Math.max(maxCount + Math.ceil(maxCount * 0.2), 1)]; // Add 20% padding, minimum 1

  return (
    <div className="space-y-6">
      {/* Sync Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Google Sheets Sync</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={() => syncApplicationsMutation.mutate(false)}
              disabled={syncApplicationsMutation.isPending}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${syncApplicationsMutation.isPending ? 'animate-spin' : ''}`} />
              Sync Applications & Reach Out
            </Button>
            <Button
              onClick={() => syncApplicationsMutation.mutate(true)}
              disabled={syncApplicationsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              Sync Applications
            </Button>
            <Button
              onClick={() => sendFollowUpsMutation.mutate(false)}
              disabled={sendFollowUpsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Send className={`h-4 w-4 ${sendFollowUpsMutation.isPending ? 'animate-spin' : ''}`} />
              Send Follow-ups
            </Button>
            <Button
              onClick={() => sendFollowUpsMutation.mutate(true)}
              disabled={sendFollowUpsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Eye className="h-4 w-4" />
              Dry Run Follow-ups
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 overflow-visible">
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

        <Card
          className="border-l-4 border-l-green-500 relative cursor-help overflow-visible"
          onMouseEnter={() => setShowInterviewTooltip(true)}
          onMouseLeave={() => setShowInterviewTooltip(false)}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-muted-foreground">Interview Rate</p>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </div>
                <p className="text-3xl font-bold">
                  {(stats.applications_reached_out ?? 0) > 0
                    ? Math.round(((stats.applications_reached_interviews ?? 0) / (stats.applications_reached_out ?? 1)) * 100)
                    : 0}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <Clock className="h-6 w-6 text-green-500" />
              </div>
            </div>
          </CardContent>
          {showInterviewTooltip && stats.interview_breakdown && (
            <div className="absolute top-full left-0 mt-2 z-[100] w-72 p-3 bg-popover border border-border rounded-lg shadow-xl text-sm pointer-events-none">
              <div className="space-y-2">
                <p className="font-semibold mb-2">Interview Breakdown</p>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span>Interview Scheduled:</span>
                    <span className="font-medium">{stats.interview_breakdown.interview_scheduled || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Interview In Progress:</span>
                    <span className="font-medium">{stats.interview_breakdown.interview_in_progress || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Result Awaited:</span>
                    <span className="font-medium">{stats.interview_breakdown.result_awaited || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Offer Received:</span>
                    <span className="font-medium">{stats.interview_breakdown.offer_received || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Accepted:</span>
                    <span className="font-medium">{stats.interview_breakdown.accepted || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Offer Rejected:</span>
                    <span className="font-medium">{stats.interview_breakdown.offer_rejected || 0}</span>
                  </div>
                  <div className="flex justify-between border-t pt-1.5 mt-1.5 text-muted-foreground">
                    <span>Rejected (after interview):</span>
                    <span className="font-medium">{stats.interview_breakdown.rejected_after_interview || 0}</span>
                  </div>
                  <div className="flex justify-between text-muted-foreground">
                    <span>Ghosted (after interview):</span>
                    <span className="font-medium">{stats.interview_breakdown.ghosted_after_interview || 0}</span>
                  </div>
                  <div className="flex justify-between text-muted-foreground">
                    <span>Withdrawn (after interview):</span>
                    <span className="font-medium">{stats.interview_breakdown.withdrawn_after_interview || 0}</span>
                  </div>
                  <div className="flex justify-between border-t pt-1.5 mt-1.5 font-semibold">
                    <span>Total Reached Interviews:</span>
                    <span>{stats.applications_reached_interviews ?? 0}</span>
                  </div>
                  <div className="flex justify-between text-muted-foreground text-xs">
                    <span>Out of Reached Out:</span>
                    <span>{stats.applications_reached_out ?? 0}</span>
                  </div>
                </div>
              </div>
              {/* Arrow pointer */}
              <div className="absolute bottom-full left-6 mb-0">
                <div className="w-3 h-3 bg-popover border-l border-t border-border rotate-45"></div>
              </div>
            </div>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Application Status Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Application Status Overview</CardTitle>
          </CardHeader>
          <CardContent className="pb-2">
            <div className="h-[468px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusBarData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
                  <XAxis
                    dataKey="status"
                    className="text-xs"
                    tick={{ fill: 'currentColor', className: 'fill-muted-foreground', fontSize: 11 }}
                  />
                  <YAxis
                    className="text-xs"
                    tick={{ fill: 'currentColor', className: 'fill-muted-foreground', fontSize: 11 }}
                    domain={yAxisDomain}
                    allowDecimals={false}
                    width={30}
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
            </div>
          </CardContent>
        </Card>

        {/* Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Initial Stages */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Initial Stages
                </h4>
                <div className="space-y-2">
                  {initialStatuses.map((statusKey) => {
                    const count = (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                    return (
                      <div key={statusKey} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: STATUS_COLORS[statusKey] || '#94a3b8' }}
                          />
                          <span className="text-sm font-medium">
                            {capitalizeFirst(statusKey.replace(/_/g, ' '))}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold">{count}</span>
                          <span className="text-xs text-muted-foreground">
                            ({stats.total_applications > 0 ? Math.round((count / stats.total_applications) * 100) : 0}%)
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Interview Process */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Interview Process
                </h4>
                <div className="space-y-2 pl-4 border-l-2 border-l-purple-500/30">
                  {interviewStatuses.map((statusKey) => {
                    const count = (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                    return (
                      <div key={statusKey} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: STATUS_COLORS[statusKey] || '#94a3b8' }}
                          />
                          <span className="text-sm font-medium">
                            {capitalizeFirst(statusKey.replace(/_/g, ' '))}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold">{count}</span>
                          <span className="text-xs text-muted-foreground">
                            ({stats.total_applications > 0 ? Math.round((count / stats.total_applications) * 100) : 0}%)
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Offer Stage */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Offer Stage
                </h4>
                <div className="space-y-2">
                  {offerStatuses.map((statusKey) => {
                    const count = (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                    return (
                      <div key={statusKey} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: STATUS_COLORS[statusKey] || '#94a3b8' }}
                          />
                          <span className="text-sm font-medium">
                            {capitalizeFirst(statusKey.replace(/_/g, ' '))}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold">{count}</span>
                          <span className="text-xs text-muted-foreground">
                            ({stats.total_applications > 0 ? Math.round((count / stats.total_applications) * 100) : 0}%)
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Final Outcomes - After Offer */}
              {(afterOfferStatuses.some(s => (stats.by_status[s as keyof typeof stats.by_status] as number) > 0)) && (
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    Final Outcomes (After Offer)
                  </h4>
                  <div className="space-y-2 pl-4 border-l-2 border-l-green-500/30">
                    {afterOfferStatuses.map((statusKey) => {
                      const count = (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                      if (count === 0) return null;
                      return (
                        <div key={statusKey} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="h-3 w-3 rounded-full"
                              style={{ backgroundColor: STATUS_COLORS[statusKey] || '#94a3b8' }}
                            />
                            <span className="text-sm font-medium">
                              {capitalizeFirst(statusKey.replace(/_/g, ' '))}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold">{count}</span>
                            <span className="text-xs text-muted-foreground">
                              ({stats.total_applications > 0 ? Math.round((count / stats.total_applications) * 100) : 0}%)
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Final Outcomes - Early Termination */}
              {(earlyTerminalStatuses.some(s => (stats.by_status[s as keyof typeof stats.by_status] as number) > 0)) && (
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                    Final Outcomes (Early Termination)
                  </h4>
                  <div className="space-y-2 pl-4 border-l-2 border-l-red-500/30">
                    {earlyTerminalStatuses.map((statusKey) => {
                      const count = (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                      if (count === 0) return null;
                      return (
                        <div key={statusKey} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="h-3 w-3 rounded-full"
                              style={{ backgroundColor: STATUS_COLORS[statusKey] || '#94a3b8' }}
                            />
                            <span className="text-sm font-medium">
                              {capitalizeFirst(statusKey.replace(/_/g, ' '))}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold">{count}</span>
                            <span className="text-xs text-muted-foreground">
                              ({stats.total_applications > 0 ? Math.round((count / stats.total_applications) * 100) : 0}%)
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
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
          {recentApps?.items?.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No applications yet.</p>
              <p className="text-sm mt-1">Start by syncing from Google Sheets!</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-3 font-semibold text-xs">Company / Position</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Status</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Last Updated</th>
                    <th className="text-left py-2 px-3 font-semibold text-xs">Emails</th>
                  </tr>
                </thead>
                <tbody>
                  {recentApps?.items?.map((app) => (
                    <tr
                      key={app.id}
                      className="border-b hover:bg-muted/50 transition-colors group"
                    >
                      <td className="py-2 px-3">
                        <Link
                          to={`/applications/${app.id}`}
                          className="group-hover:text-primary transition-colors"
                        >
                          <div className="font-semibold">{app.company_name}</div>
                          <div className="text-sm text-muted-foreground">{app.position}</div>
                        </Link>
                      </td>
                      <td className="py-2 px-3">
                        <StatusBadge status={app.status} size="sm" />
                      </td>
                      <td className="py-2 px-3 text-xs text-muted-foreground">
                        {formatDateTime(app.updated_at)}
                      </td>
                      <td className="py-2 px-3">
                        {app.emails_count !== undefined && app.emails_count > 0 ? (
                          <span className="flex items-center gap-1 text-xs">
                            <Mail className="h-3 w-3" />
                            {app.emails_count}
                          </span>
                        ) : (
                          <span className="text-xs text-muted-foreground">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

