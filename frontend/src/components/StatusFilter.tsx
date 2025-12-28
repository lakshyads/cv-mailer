import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Filter, ChevronDown, X } from 'lucide-react';
import { ALL_JOB_STATUSES, STATUS_LABELS } from '@/lib/constants';
import type { JobStatus } from '@/types';

interface StatusFilterProps {
  selectedStatuses: JobStatus[];
  onStatusChange: (statuses: JobStatus[]) => void;
  onClear?: () => void;
}

/**
 * Reusable status filter component with multi-select dropdown.
 */
export function StatusFilter({ selectedStatuses, onStatusChange, onClear }: StatusFilterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (filterRef.current && !filterRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleStatus = (status: JobStatus) => {
    if (selectedStatuses.includes(status)) {
      onStatusChange(selectedStatuses.filter(s => s !== status));
    } else {
      onStatusChange([...selectedStatuses, status]);
    }
  };

  const hasActiveFilters = selectedStatuses.length > 0;

  return (
    <div className="relative" ref={filterRef}>
      <Button
        variant={hasActiveFilters ? 'default' : 'outline'}
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="h-8"
      >
        <Filter className="h-3 w-3 mr-1.5" />
        Status {hasActiveFilters && `(${selectedStatuses.length})`}
        <ChevronDown className={`h-3 w-3 ml-1.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 z-50 bg-popover border border-border rounded-lg shadow-lg min-w-[200px] max-h-[300px] overflow-y-auto">
          <div className="p-2 space-y-1">
            {ALL_JOB_STATUSES.map((status) => {
              const isSelected = selectedStatuses.includes(status);
              return (
                <label
                  key={status}
                  className="flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-muted cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleStatus(status)}
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="text-sm flex-1">
                    {STATUS_LABELS[status]}
                  </span>
                </label>
              );
            })}
          </div>
          {hasActiveFilters && onClear && (
            <div className="border-t p-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  onClear();
                  setIsOpen(false);
                }}
                className="w-full h-8"
              >
                <X className="h-3 w-3 mr-1.5" />
                Clear
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

