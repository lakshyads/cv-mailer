import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { ApplicationsTableRow } from '@/components/organisms/applications/ApplicationsTableRow';
import { Link } from 'react-router-dom';
import { Briefcase, ArrowUpRight } from 'lucide-react';
import type { Application } from '@/types';

interface RecentApplicationsProps {
  applications?: Application[];
}

/**
 * Recent applications section component.
 * Uses the shared ApplicationTableRow component for consistency.
 */
export function RecentApplications({ applications }: RecentApplicationsProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            Recently Updated Applications
            <span className="text-sm font-medium flex items-center gap-1">
              (Top {applications?.length} by last updated)
            </span>
          </CardTitle>
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
        {!applications || applications.length === 0 ? (
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
                  <th className="text-left py-2 px-3 font-semibold text-xs">Status</th>
                  <th className="text-left py-2 px-3 font-semibold text-xs">
                    Company / Position
                  </th>
                  <th className="text-left py-2 px-3 font-semibold text-xs">Created At</th>
                  <th className="text-left py-2 px-3 font-semibold text-xs">Last Updated</th>
                  <th className="text-left py-2 px-3 font-semibold text-xs">Emails</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <ApplicationsTableRow
                    key={app.id}
                    application={app}
                    size="sm"
                    showCreatedAt={true}
                    showActions={false}
                    showLocation={true}
                    showJobUrl={false}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

