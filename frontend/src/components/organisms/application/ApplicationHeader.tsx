import { Link } from 'react-router-dom';
import { Button } from '@/components/atoms/ui/Button';
import { StatusBadge } from '@/components/atoms/StatusBadge';
import { ArrowLeft } from 'lucide-react';
import type { Application } from '@/types';

interface ApplicationHeaderProps {
    application: Application;
}

/**
 * Application header component with back button, company/position, and status badge.
 */
export function ApplicationHeader({ application }: ApplicationHeaderProps) {
    return (
        <div className="flex flex-wrap items-start gap-4">
            <Link to="/applications">
                <Button variant="ghost" size="icon">
                    <ArrowLeft className="h-5 w-5" />
                </Button>
            </Link>
            <div className="flex-1 min-w-0">
                <h2 className="text-3xl font-bold tracking-tight">{application.company_name}</h2>
                <p className="text-lg text-muted-foreground mt-1">{application.position}</p>
            </div>
            <StatusBadge status={application.status} />
        </div>
    );
}

