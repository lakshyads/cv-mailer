import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { CHART_STATUS_COLORS } from '@/lib/chartUtils';
import { capitalizeFirst } from '@/lib/utils';
import type { Statistics } from '@/types';

interface StatusBreakdownProps {
    stats: Statistics;
}

/**
 * Status breakdown component showing detailed status statistics.
 */
export function StatusBreakdown({ stats }: StatusBreakdownProps) {
    const interviewStatuses = ['interview_scheduled', 'interview_in_progress', 'result_awaited'];
    const offerStatuses = ['offer_received'];
    const afterOfferStatuses = ['accepted', 'offer_rejected'];
    const earlyTerminalStatuses = ['rejected', 'ghosted', 'withdrawn'];

    return (
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
                                    <span className="text-sm font-bold">
                                        {stats.total_applications_applied ?? stats.total_applications ?? 0}
                                    </span>
                                    <span className="text-xs text-muted-foreground">(100% of total)</span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div
                                        className="h-3 w-3 rounded-full"
                                        style={{ backgroundColor: CHART_STATUS_COLORS['applied'] || '#60a5fa' }}
                                    />
                                    <span className="text-sm font-medium">Only Applied</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold">
                                        {stats.applications_currently_applied ?? 0}
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                        (
                                        {(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0
                                            ? Math.round(
                                                ((stats.applications_currently_applied ?? 0) /
                                                    (stats.total_applications_applied ?? stats.total_applications ?? 1)) *
                                                100
                                            )
                                            : 0}
                                        % of total applied)
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
                                        (
                                        {(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0
                                            ? Math.round(
                                                ((stats.applications_reached_out ?? 0) /
                                                    (stats.total_applications_applied ?? stats.total_applications ?? 1)) *
                                                100
                                            )
                                            : 0}
                                        % of total applied)
                                    </span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div
                                        className="h-3 w-3 rounded-full"
                                        style={{ backgroundColor: CHART_STATUS_COLORS['reached_out'] || '#818cf8' }}
                                    />
                                    <span className="text-sm font-medium">Only Reached Out</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold">
                                        {stats.applications_currently_reached_out ?? 0}
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                        (
                                        {(stats.applications_reached_out ?? 0) > 0
                                            ? Math.round(
                                                ((stats.applications_currently_reached_out ?? 0) /
                                                    (stats.applications_reached_out ?? 1)) *
                                                100
                                            )
                                            : 0}
                                        % of total reached out)
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
                                    <span className="text-sm font-bold">
                                        {stats.applications_reached_interviews ?? 0}
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                        (
                                        {(stats.total_applications_applied ?? stats.total_applications ?? 0) > 0
                                            ? Math.round(
                                                ((stats.applications_reached_interviews ?? 0) /
                                                    (stats.total_applications_applied ?? stats.total_applications ?? 1)) *
                                                100
                                            )
                                            : 0}
                                        % of total applied)
                                    </span>
                                </div>
                            </div>
                            {interviewStatuses.map((statusKey) => {
                                const count =
                                    (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                                return (
                                    <div key={statusKey} className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="h-3 w-3 rounded-full"
                                                style={{
                                                    backgroundColor: CHART_STATUS_COLORS[statusKey] || '#94a3b8',
                                                }}
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
                                    <span className="text-sm font-bold">
                                        {stats.applications_reached_offers ?? 0}
                                    </span>
                                    <span className="text-xs text-muted-foreground">
                                        (
                                        {stats.total_applications > 0
                                            ? Math.round(
                                                ((stats.applications_reached_offers ?? 0) / stats.total_applications) * 100
                                            )
                                            : 0}
                                        % of total)
                                    </span>
                                </div>
                            </div>
                            {offerStatuses.map((statusKey) => {
                                const count =
                                    (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                                return (
                                    <div key={statusKey} className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="h-3 w-3 rounded-full"
                                                style={{
                                                    backgroundColor: CHART_STATUS_COLORS[statusKey] || '#94a3b8',
                                                }}
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
                                const count =
                                    (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                                if (count === 0) return null;
                                return (
                                    <div key={statusKey} className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div
                                                className="h-3 w-3 rounded-full"
                                                style={{
                                                    backgroundColor: CHART_STATUS_COLORS[statusKey] || '#94a3b8',
                                                }}
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
                    {earlyTerminalStatuses.some(
                        (s) => (stats.by_status[s as keyof typeof stats.by_status] as number) > 0
                    ) && (
                            <div>
                                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                                    Final Outcomes (Early Termination)
                                </h4>
                                <div className="space-y-2 pl-4 border-l-2 border-l-red-500/30">
                                    {earlyTerminalStatuses.map((statusKey) => {
                                        const count =
                                            (stats.by_status[statusKey as keyof typeof stats.by_status] as number) || 0;
                                        if (count === 0) return null;
                                        return (
                                            <div key={statusKey} className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <div
                                                        className="h-3 w-3 rounded-full"
                                                        style={{
                                                            backgroundColor: CHART_STATUS_COLORS[statusKey] || '#94a3b8',
                                                        }}
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
    );
}

