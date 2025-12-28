import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { User } from 'lucide-react';
import type { Application } from '@/types';

interface RecruitersCardProps {
  recruiters: Application['recruiters'];
}

/**
 * Recruiters card component.
 * Displays list of recruiters associated with an application.
 */
export function RecruitersCard({ recruiters }: RecruitersCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recruiters</CardTitle>
      </CardHeader>
      <CardContent>
        {recruiters && recruiters.length > 0 ? (
          <div className="space-y-3">
            {recruiters.map((recruiter) => (
              <Link
                key={recruiter.id}
                to={`/recruiters/${recruiter.id}`}
                className="flex items-start gap-3 rounded-lg border p-3 hover:bg-gray-50 transition-colors"
              >
                <User className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">{recruiter.name}</p>
                  <p className="text-xs text-muted-foreground truncate">{recruiter.email}</p>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No recruiters assigned</p>
        )}
      </CardContent>
    </Card>
  );
}

