import { Badge } from './ui/Badge';
import { getStatusColor, capitalizeFirst } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${getStatusColor(status)}`}>
      {capitalizeFirst(status)}
    </span>
  );
}

