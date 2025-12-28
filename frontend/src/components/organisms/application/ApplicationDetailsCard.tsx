import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { DetailRow } from '@/components/molecules/DetailRow';
import { MapPin, DollarSign, ExternalLink, Calendar, FileText } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';
import type { Application } from '@/types';

interface ApplicationDetailsCardProps {
  application: Application;
}

/**
 * Application details card component.
 * Displays location, salary, job posting, timeline, custom message, and notes.
 */
export function ApplicationDetailsCard({ application: app }: ApplicationDetailsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Application Details</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {app.location && (
          <DetailRow icon={MapPin} label="Location" value={app.location} />
        )}

        {app.expected_salary && (
          <DetailRow icon={DollarSign} label="Expected Salary" value={app.expected_salary} />
        )}

        {app.job_posting_url && (
          <DetailRow
            icon={ExternalLink}
            label="Job Posting"
            value={
              <a
                href={app.job_posting_url.startsWith('http') ? app.job_posting_url : `https://${app.job_posting_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                View Posting
                <ExternalLink className="h-3 w-3" />
              </a>
            }
          />
        )}

        <DetailRow
          icon={Calendar}
          label="Timeline"
          value={
            <div className="text-sm text-muted-foreground space-y-1">
              <p>Created: {formatDateTime(app.created_at)}</p>
              {app.applied_at && <p>Applied: {formatDateTime(app.applied_at)}</p>}
              {app.updated_at && <p>Last Updated: {formatDateTime(app.updated_at)}</p>}
              {app.closed_at && <p>Closed: {formatDateTime(app.closed_at)}</p>}
            </div>
          }
        />

        {app.custom_message && (
          <DetailRow icon={FileText} label="Custom Message" value={app.custom_message} />
        )}

        {app.notes && (
          <DetailRow icon={FileText} label="Notes" value={app.notes} />
        )}
      </CardContent>
    </Card>
  );
}

