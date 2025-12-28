import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';

type SortField = 'created_at' | 'updated_at' | 'status' | null;
type SortOrder = 'asc' | 'desc';

interface SortableTableHeaderProps {
  field: SortField;
  currentSort: SortField;
  currentOrder: SortOrder;
  onSort: (field: SortField) => void;
  children: React.ReactNode;
  className?: string;
}

/**
 * Reusable sortable table header component.
 * Provides consistent sorting UI across tables.
 */
export function SortableTableHeader({
  field,
  currentSort,
  currentOrder,
  onSort,
  children,
  className = '',
}: SortableTableHeaderProps) {
  const getSortIcon = () => {
    if (currentSort !== field) {
      return <ArrowUpDown className="h-3 w-3 text-muted-foreground" />;
    }
    return currentOrder === 'asc' ? (
      <ArrowUp className="h-3 w-3" />
    ) : (
      <ArrowDown className="h-3 w-3" />
    );
  };

  return (
    <th className={`text-left py-3 px-4 font-semibold text-sm ${className}`}>
      <button
        onClick={() => onSort(field)}
        className="flex items-center gap-2 hover:text-primary transition-colors"
      >
        {children}
        {field && getSortIcon()}
      </button>
    </th>
  );
}

