import { Card, CardContent } from '@/components/ui/Card';
import { LucideIcon } from 'lucide-react';
import { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number | ReactNode;
  icon: LucideIcon;
  iconColor?: string;
  borderColor?: string;
  colSpan?: number;
  tooltip?: ReactNode;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

/**
 * Reusable stat card component for displaying statistics.
 * Used in dashboard and other pages to show key metrics.
 */
const colSpanClasses: Record<number, string> = {
  1: 'lg:col-span-1',
  2: 'lg:col-span-2',
  3: 'lg:col-span-3',
  4: 'lg:col-span-4',
  5: 'lg:col-span-5',
  6: 'lg:col-span-6',
};

export function StatCard({
  title,
  value,
  icon: Icon,
  iconColor = 'text-primary',
  borderColor = 'border-l-primary',
  colSpan = 1,
  tooltip,
  onMouseEnter,
  onMouseLeave,
}: StatCardProps) {
  return (
    <Card
      className={`${borderColor} relative cursor-help overflow-visible ${colSpanClasses[colSpan] || colSpanClasses[1]}`}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            {typeof value === 'string' || typeof value === 'number' ? (
              <p className="text-3xl font-bold">{value}</p>
            ) : (
              <div>{value}</div>
            )}
          </div>
          <div className={`h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 ml-4`}>
            <Icon className={`h-6 w-6 ${iconColor}`} />
          </div>
        </div>
      </CardContent>
      {tooltip}
    </Card>
  );
}

