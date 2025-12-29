import { getStatusBadgeColor } from '@/lib/statusColors';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

// Legacy status mappings for backward compatibility
const LEGACY_STATUS_MAP: Record<string, string> = {
  interviewing: 'interview_scheduled',
  offer: 'offer_received',
};

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const sizeClass = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm';
  
  // Map legacy statuses to current ones
  const normalizedStatus = LEGACY_STATUS_MAP[status.toLowerCase()] || status;
  const statusClass = getStatusBadgeColor(normalizedStatus);
  
  const displayText = status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  
  return (
    <span className={`inline-flex items-center rounded-full font-semibold ${sizeClass} ${statusClass}`}>
      {displayText}
    </span>
  );
}

