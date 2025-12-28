import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { statisticsApi, applicationsApi } from '@/api/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingScreen } from '@/components/ui/Spinner';
import { StatusBadge } from '@/components/StatusBadge';
import { GoogleSheetsSync } from '@/components/GoogleSheetsSync';
import { formatDateTime, capitalizeFirst } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { Briefcase, Mail, TrendingUp, Clock, ArrowUpRight, Info } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

import { getStatusSolidColor } from '@/lib/statusColors';

// Status colors for charts - includes special aggregate keys
// Uses shared status colors from statusColors.ts for consistency
const STATUS_COLORS: Record<string, string> = {
  // Special aggregate keys (not actual statuses)
  total_applied: '#3b82f6',        // Blue - total applications applied
  total_reached_out: '#6366f1',    // Indigo - total reached out
  total_reached_interviews: '#8b5cf6', // Purple - total reached interviews
  total_offers_received: '#10b981', // Green - total offers received
  // Actual status colors from shared utility
  applied: getStatusSolidColor('applied'),
  reached_out: getStatusSolidColor('reached_out'),
  interview_scheduled: getStatusSolidColor('interview_scheduled'),
  interview_in_progress: getStatusSolidColor('interview_in_progress'),
  result_awaited: getStatusSolidColor('result_awaited'),
  offer_received: getStatusSolidColor('offer_received'),
  accepted: getStatusSolidColor('accepted'),
  rejected: getStatusSolidColor('rejected'),
  ghosted: getStatusSolidColor('ghosted'),
  withdrawn: getStatusSolidColor('withdrawn'),
  offer_rejected: getStatusSolidColor('offer_rejected'),
  draft: getStatusSolidColor('draft'),
};

// Status order is now defined inline in the component for better organization

export default function DashboardPage() {
  const [showInterviewTooltip, setShowInterviewTooltip] = useState(false);
  const [showOfferTooltip, setShowOfferTooltip] = useState(false);

  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => statisticsApi.get(),
  });

  const { data: recentApps } = useQuery({
    queryKey: ['applications', 'recent'],
    queryFn: () => applicationsApi.list({
      limit: 10,
      sort_by: 'updated_at',
      order: 'desc'
    }),
  });

  if (isLoading || !stats) {
    return <LoadingScreen />;
  }

  // Prepare data for charts - ordered by logical flow
  // Initial stages (currently at status)
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

  // Chart data in logical order: 
  // total applied → currently applied → total reached out → currently reached out → 
  // total reached interviews → interview stages → total offers received → offer stages → 
  // after offer → early termination
  const chartOrder = [
    'total_applied', // Special: total applications applied
    'applied', // Currently at applied
    'total_reached_out', // Special: total applications reached out
    'reached_out', // Currently at reached out
    'total_reached_interviews', // Special: total reached interviews
    ...interviewStatuses,
    ...earlyTerminalStatuses,
    'total_offers_received', // Special: total offers received
    ...offerStatuses,
    ...afterOfferStatuses,
  ];

  const statusBarData = chartOrder.map((statusKey) => {
    if (statusKey === 'total_applied') {
      return {
        status: 'Total Applied',
        statusKey: 'total_applied',
        count: stats.total_applications_applied ?? stats.total_applications ?? 0,
      };
    }
    if (statusKey === 'total_reached_out') {
      return {
        status: 'Total Reached Out',
        statusKey: 'total_reached_out',
        count: stats.applications_reached_out ?? 0,
      };
    }
    if (statusKey === 'total_reached_interviews') {
      return {
        status: 'Total Reached Interviews',
        statusKey: 'total_reached_interviews',
        count: stats.applications_reached_interviews ?? 0,
      };
    }
    if (statusKey === 'total_offers_received') {
      return {
        status: 'Total Offers Received',
        statusKey: 'total_offers_received',
        count: stats.applications_reached_offers ?? 0,
      };
    }
    return {
      status: capitalizeFirst(statusKey.replace(/_/g, ' ')),
      statusKey,
      count: (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0,
    };
  }).filter((item) => {
    // Always show special totals and main flow statuses, only show terminal if count > 0
    if (item.statusKey === 'total_applied' ||
      item.statusKey === 'total_reached_out' ||
      item.statusKey === 'total_reached_interviews' ||
      item.statusKey === 'total_offers_received') {
      return true; // Always show totals
    }
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
      <GoogleSheetsSync />

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6 overflow-visible">
        <Card className="border-l-4 border-l-primary lg:col-span-1">
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

        <Card className="border-l-4 border-l-blue-500 lg:col-span-1">
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

        <Card className="border-l-4 border-l-purple-500 lg:col-span-1">
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
          className="border-l-4 border-l-green-500 relative cursor-help overflow-visible lg:col-span-1"
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
                  {(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0
                    ? Math.round(((stats.applications_reached_interviews ?? 0) / (stats.total_applications_applied ?? stats.total_applications ?? 1)) * 100)
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
                    <span>Out of Total Applied:</span>
                    <span>{stats.total_applications_applied ?? stats.total_applications ?? 0}</span>
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

        <Card
          className="border-l-4 border-l-emerald-500 relative cursor-help overflow-visible lg:col-span-2"
          onMouseEnter={() => setShowOfferTooltip(true)}
          onMouseLeave={() => setShowOfferTooltip(false)}
        >
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-muted-foreground">Offer Rate</p>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <p className="text-3xl font-bold">
                      {(stats.applications_reached_interviews ?? 0) > 0
                        ? Math.round(((stats.applications_reached_offers ?? 0) / (stats.applications_reached_interviews ?? 1)) * 100)
                        : 0}%
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      of interviews
                    </p>
                  </div>
                  <div className="h-8 w-px bg-border"></div>
                  <div className="flex-1">
                    <p className="text-3xl font-bold">
                      {stats.total_applications > 0
                        ? Math.round(((stats.applications_reached_offers ?? 0) / stats.total_applications) * 100)
                        : 0}%
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      of total
                    </p>
                  </div>
                </div>
              </div>
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center ml-4">
                <TrendingUp className="h-6 w-6 text-emerald-500" />
              </div>
            </div>
          </CardContent>
          {showOfferTooltip && (
            <div className="absolute top-full left-0 mt-2 z-[100] w-72 p-3 bg-popover border border-border rounded-lg shadow-xl text-sm pointer-events-none">
              <div className="space-y-2">
                <p className="font-semibold mb-2">Offer Rate Details</p>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span>Total Reached Offers:</span>
                    <span className="font-medium">{stats.applications_reached_offers ?? 0}</span>
                  </div>
                  <div className="flex justify-between text-muted-foreground">
                    <span>Out of Reached Interviews:</span>
                    <span>{stats.applications_reached_interviews ?? 0}</span>
                  </div>
                  <div className="flex justify-between text-muted-foreground">
                    <span>Out of Total Applications:</span>
                    <span>{stats.total_applications}</span>
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
            <div className="h-[606px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={statusBarData} margin={{ top: 10, right: 20, left: 10, bottom: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
                  <XAxis
                    dataKey="status"
                    className="text-xs"
                    interval={0}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fill: 'currentColor', className: 'fill-muted-foreground', fontSize: 10 }}
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
              {/* Applied Summary */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Applied Summary
                </h4>
                <div className="space-y-2 pl-4 border-l-2 border-l-blue-500/30">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Total Applied</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.total_applications_applied ?? stats.total_applications ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        (100% of total)
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="h-3 w-3 rounded-full"
                        style={{ backgroundColor: STATUS_COLORS['applied'] || '#60a5fa' }}
                      />
                      <span className="text-sm font-medium">Only Applied</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.applications_currently_applied ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0 ? Math.round(((stats.applications_currently_applied ?? 0) / (stats.total_applications_applied ?? stats.total_applications ?? 1)) * 100) : 0}% of total applied)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Reached Out Summary */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Reached Out Summary
                </h4>
                <div className="space-y-2 pl-4 border-l-2 border-l-indigo-500/30">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Total Reached Out</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.applications_reached_out ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0 ? Math.round(((stats.applications_reached_out ?? 0) / (stats.total_applications_applied ?? stats.total_applications ?? 1)) * 100) : 0}% of total applied)
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="h-3 w-3 rounded-full"
                        style={{ backgroundColor: STATUS_COLORS['reached_out'] || '#818cf8' }}
                      />
                      <span className="text-sm font-medium">Only Reached Out</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.applications_currently_reached_out ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(stats.applications_reached_out ?? 0) > 0 ? Math.round(((stats.applications_currently_reached_out ?? 0) / (stats.applications_reached_out ?? 1)) * 100) : 0}% of total reached out)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Interview Summary */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Interview Summary
                </h4>
                <div className="space-y-2 pl-4 border-l-2 border-l-purple-500/30">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Total Reached Interviews</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.applications_reached_interviews ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0 ? Math.round(((stats.applications_reached_interviews ?? 0) / (stats.total_applications_applied ?? stats.total_applications ?? 1)) * 100) : 0}% of total applied)
                      </span>
                    </div>
                  </div>
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

              {/* Offer Summary */}
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                  Offer Summary
                </h4>
                <div className="space-y-2 pl-4 border-l-2 border-l-green-500/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">Total Offers Received</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold">{stats.applications_reached_offers ?? 0}</span>
                      <span className="text-xs text-muted-foreground">
                        ({stats.total_applications > 0 ? Math.round(((stats.applications_reached_offers ?? 0) / stats.total_applications) * 100) : 0}% of total)
                      </span>
                    </div>
                  </div>
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
            <CardTitle>Recently Updated Applications (Top 10)</CardTitle>
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

