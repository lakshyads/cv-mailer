import { useState } from 'react';
import { StatCard } from '@/components/StatCard';
import { Tooltip } from '@/components/Tooltip';
import { Briefcase, Mail, TrendingUp, Clock } from 'lucide-react';
import type { Statistics } from '@/types';

interface StatsOverviewProps {
    stats: Statistics;
}

/**
 * Stats overview section showing key metrics cards.
 */
export function StatsOverview({ stats }: StatsOverviewProps) {
    const [showInterviewTooltip, setShowInterviewTooltip] = useState(false);
    const [showOfferTooltip, setShowOfferTooltip] = useState(false);

    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6 overflow-visible">
            <StatCard
                title="Total Applications"
                value={stats.total_applications}
                icon={Briefcase}
                iconColor="text-primary"
                borderColor="border-l-primary"
                colSpan={1}
            />

            <StatCard
                title="Emails Sent"
                value={stats.total_emails_sent}
                icon={Mail}
                iconColor="text-blue-500"
                borderColor="border-l-blue-500"
                colSpan={1}
            />

            <StatCard
                title="Follow-ups"
                value={stats.follow_ups_sent}
                icon={TrendingUp}
                iconColor="text-purple-500"
                borderColor="border-l-purple-500"
                colSpan={1}
            />

            <StatCard
                title="Interview Rate"
                value={
                    (stats.total_applications_applied ?? stats.total_applications ?? 0) > 0
                        ? `${Math.round(
                            ((stats.applications_reached_interviews ?? 0) /
                                (stats.total_applications_applied ?? stats.total_applications ?? 1)) *
                            100
                        )}%`
                        : '0%'
                }
                icon={Clock}
                iconColor="text-green-500"
                borderColor="border-l-green-500"
                colSpan={1}
                onMouseEnter={() => setShowInterviewTooltip(true)}
                onMouseLeave={() => setShowInterviewTooltip(false)}
                tooltip={
                    showInterviewTooltip && stats.interview_breakdown ? (
                        <Tooltip>
                            <div className="space-y-2">
                                <p className="font-semibold mb-2">Interview Breakdown</p>
                                <div className="space-y-1.5 text-xs">
                                    <div className="flex justify-between">
                                        <span>Interview Scheduled:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.interview_scheduled || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Interview In Progress:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.interview_in_progress || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Result Awaited:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.result_awaited || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Offer Received:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.offer_received || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Accepted:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.accepted || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Offer Rejected:</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.offer_rejected || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between border-t pt-1.5 mt-1.5 text-muted-foreground">
                                        <span>Rejected (after interview):</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.rejected_after_interview || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-muted-foreground">
                                        <span>Ghosted (after interview):</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.ghosted_after_interview || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-muted-foreground">
                                        <span>Withdrawn (after interview):</span>
                                        <span className="font-medium">
                                            {stats.interview_breakdown.withdrawn_after_interview || 0}
                                        </span>
                                    </div>
                                    <div className="flex justify-between border-t pt-1.5 mt-1.5 font-semibold">
                                        <span>Total Reached Interviews:</span>
                                        <span>{stats.applications_reached_interviews ?? 0}</span>
                                    </div>
                                    <div className="flex justify-between text-muted-foreground text-xs">
                                        <span>Out of Total Applied:</span>
                                        <span>
                                            {stats.total_applications_applied ?? stats.total_applications ?? 0}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </Tooltip>
                    ) : undefined
                }
            />

            <StatCard
                title="Offer Rate"
                value={
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <p className="text-3xl font-bold">
                                {(stats.applications_reached_interviews ?? 0) > 0
                                    ? Math.round(
                                        ((stats.applications_reached_offers ?? 0) /
                                            (stats.applications_reached_interviews ?? 1)) *
                                        100
                                    )
                                    : 0}
                                %
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">of interviews</p>
                        </div>
                        <div className="h-8 w-px bg-border"></div>
                        <div className="flex-1">
                            <p className="text-3xl font-bold">
                                {stats.total_applications > 0
                                    ? Math.round(
                                        ((stats.applications_reached_offers ?? 0) / stats.total_applications) * 100
                                    )
                                    : 0}
                                %
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">of total</p>
                        </div>
                    </div>
                }
                icon={TrendingUp}
                iconColor="text-emerald-500"
                borderColor="border-l-emerald-500"
                colSpan={2}
                onMouseEnter={() => setShowOfferTooltip(true)}
                onMouseLeave={() => setShowOfferTooltip(false)}
                tooltip={
                    showOfferTooltip ? (
                        <Tooltip>
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
                        </Tooltip>
                    ) : undefined
                }
            />
        </div>
    );
}

