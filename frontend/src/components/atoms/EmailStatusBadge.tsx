import { capitalizeFirst } from '@/lib/utils';
import type { EmailStatus } from '@/types';

interface EmailStatusBadgeProps {
  status: EmailStatus;
}

/**
 * Email status badge component.
 * Displays email status with appropriate colors.
 */
export function EmailStatusBadge({ status }: EmailStatusBadgeProps) {
  const statusClasses = {
    sent: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    draft: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    bounced: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${
        statusClasses[status] || statusClasses.draft
      }`}
    >
      {capitalizeFirst(status)}
    </span>
  );
}

