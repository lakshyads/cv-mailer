import { useQuery } from '@tanstack/react-query';
import { statisticsApi, applicationsApi } from '@/api/client';
import { LoadingScreen } from '@/components/ui/Spinner';
import { GoogleSheetsSync } from '@/components/GoogleSheetsSync';
import { StatsOverview } from '@/components/dashboard/StatsOverview';
import { StatusChart } from '@/components/dashboard/StatusChart';
import { StatusBreakdown } from '@/components/dashboard/StatusBreakdown';
import { RecentApplications } from '@/components/dashboard/RecentApplications';

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => statisticsApi.get(),
  });

  const { data: recentApps } = useQuery({
    queryKey: ['applications', 'recent'],
    queryFn: () =>
      applicationsApi.list({
        limit: 10,
        sort_by: 'updated_at',
        order: 'desc',
      }),
  });

  if (isLoading || !stats) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* Sync Controls */}
      <GoogleSheetsSync />

      {/* Stats Overview */}
      <StatsOverview stats={stats} />

      {/* Chart and Breakdown */}
      <div className="grid gap-4 lg:grid-cols-3">
        <StatusChart stats={stats} />
        <StatusBreakdown stats={stats} />
      </div>

      {/* Recent Applications */}
      <RecentApplications applications={recentApps?.items} />
    </div>
  );
}
