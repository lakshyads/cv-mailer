import { StatusBadge } from '@/components/atoms/StatusBadge';
import { formatDateTime } from '@/lib/utils';
import { Link } from 'react-router-dom';
import { ExternalLink, Mail, ChevronDown, ChevronRight } from 'lucide-react';
import type { Application } from '@/types';
import { ReactNode } from 'react';

interface ApplicationsTableRowProps {
    application: Application;
    showExpandButton?: boolean;
    isExpanded?: boolean;
    onToggleExpand?: () => void;
    showCreatedAt?: boolean;
    showActions?: boolean;
    showLocation?: boolean;
    showJobUrl?: boolean;
    size?: 'sm' | 'md';
    actions?: ReactNode; // Custom actions column content
}

/**
 * Reusable application table row component.
 * Renders a single application row with configurable columns and features.
 */
export function ApplicationsTableRow({
    application: app,
    showExpandButton = false,
    isExpanded = false,
    onToggleExpand,
    showCreatedAt = false,
    showActions = false,
    showLocation = true,
    showJobUrl = true,
    size = 'md',
    actions,
}: ApplicationsTableRowProps) {
    const paddingClass = size === 'sm' ? 'py-2 px-3' : 'py-3 px-4';
    const textSizeClass = size === 'sm' ? 'text-xs' : 'text-sm';

    return (
        <tr className="border-b hover:bg-muted/50 transition-colors group">
            {showExpandButton && (
                <td className={paddingClass}>
                    <button
                        onClick={onToggleExpand}
                        className="p-1 hover:bg-muted rounded transition-colors"
                        aria-label={isExpanded ? 'Collapse row' : 'Expand row'}
                    >
                        {isExpanded ? (
                            <ChevronDown className="h-4 w-4 text-muted-foreground" />
                        ) : (
                            <ChevronRight className="h-4 w-4 text-muted-foreground" />
                        )}
                    </button>
                </td>
            )}
            <td className={paddingClass}>
                <Link
                    to={`/applications/${app.id}`}
                    className={`flex items-center gap-2 group-hover:text-primary transition-colors ${size === 'sm' ? '' : ''}`}
                >
                    <div className="min-w-0">
                        <div className="flex items-center gap-2">
                            <span className={`font-semibold truncate ${size === 'sm' ? 'text-sm' : ''}`}>
                                {app.company_name}
                            </span>
                            {showJobUrl && app.job_posting_url && (
                                <a
                                    href={
                                        app.job_posting_url.startsWith('http')
                                            ? app.job_posting_url
                                            : `https://${app.job_posting_url}`
                                    }
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className="text-primary hover:text-primary/80 flex-shrink-0"
                                >
                                    <ExternalLink className="h-3 w-3" />
                                </a>
                            )}
                        </div>
                        <div className={`text-muted-foreground truncate ${textSizeClass}`}>
                            {app.position}
                        </div>
                        {showLocation && app.location && (
                            <div className={`text-muted-foreground truncate ${size === 'sm' ? 'text-xs' : 'text-xs'}`}>
                                {app.location}
                            </div>
                        )}
                    </div>
                </Link>
            </td>
            <td className={paddingClass}>
                <StatusBadge status={app.status} size={size} />
            </td>
            {showCreatedAt && (
                <td className={`${paddingClass} ${textSizeClass} text-muted-foreground`}>
                    {formatDateTime(app.created_at)}
                </td>
            )}
            <td className={`${paddingClass} ${textSizeClass} text-muted-foreground`}>
                {formatDateTime(app.updated_at)}
            </td>
            <td className={paddingClass}>
                {app.emails_count !== undefined && app.emails_count > 0 ? (
                    <span className={`flex items-center gap-1 ${textSizeClass}`}>
                        <Mail className={size === 'sm' ? 'h-3 w-3' : 'h-4 w-4'} />
                        {app.emails_count}
                    </span>
                ) : (
                    <span className={`${textSizeClass} text-muted-foreground`}>-</span>
                )}
            </td>
            {showActions && (
                <td className={`${paddingClass} text-right`}>
                    {actions}
                </td>
            )}
        </tr>
    );
}

