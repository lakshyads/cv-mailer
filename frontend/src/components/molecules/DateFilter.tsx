import { Button } from '@/components/atoms/ui/Button';
import { Calendar, Clock, X } from 'lucide-react';

type DateFilterType = 'today' | 'this_week' | 'this_month' | null;

interface DateFilterProps {
  value: DateFilterType;
  onChange: (value: DateFilterType) => void;
  onClear?: () => void;
}

/**
 * Reusable date filter component with quick filter buttons.
 */
export function DateFilter({ value, onChange, onClear }: DateFilterProps) {
  const hasActiveFilter = value !== null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm font-medium text-muted-foreground">Quick Filters:</span>
      <Button
        variant={value === 'today' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onChange(value === 'today' ? null : 'today')}
        className="h-8"
      >
        <Calendar className="h-3 w-3 mr-1.5" />
        Today
      </Button>
      <Button
        variant={value === 'this_week' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onChange(value === 'this_week' ? null : 'this_week')}
        className="h-8"
      >
        <Clock className="h-3 w-3 mr-1.5" />
        This Week
      </Button>
      <Button
        variant={value === 'this_month' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onChange(value === 'this_month' ? null : 'this_month')}
        className="h-8"
      >
        <Calendar className="h-3 w-3 mr-1.5" />
        This Month
      </Button>
      {hasActiveFilter && onClear && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="h-8 ml-auto"
        >
          <X className="h-3 w-3 mr-1.5" />
          Clear All Filters
        </Button>
      )}
    </div>
  );
}

