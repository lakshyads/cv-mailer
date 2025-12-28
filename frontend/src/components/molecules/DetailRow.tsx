import { LucideIcon } from 'lucide-react';
import { ReactNode } from 'react';

interface DetailRowProps {
  icon: LucideIcon;
  label: string;
  value?: ReactNode;
  children?: ReactNode;
  className?: string;
}

/**
 * Reusable detail row component for displaying icon, label, and value.
 * Used in application detail pages for consistent formatting.
 */
export function DetailRow({ icon: Icon, label, value, children, className = '' }: DetailRowProps) {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      <Icon className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{label}</p>
        {value && <p className="text-sm text-muted-foreground whitespace-pre-wrap">{value}</p>}
        {children}
      </div>
    </div>
  );
}

