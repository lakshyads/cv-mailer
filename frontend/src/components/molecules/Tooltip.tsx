import { ReactNode } from 'react';

interface TooltipProps {
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

/**
 * Reusable tooltip component.
 * Provides consistent tooltip styling across the application.
 */
export function Tooltip({ children, position = 'bottom', className = '' }: TooltipProps) {
  const positionClasses = {
    top: 'bottom-full left-0 mb-2',
    bottom: 'top-full left-0 mt-2',
    left: 'right-full top-0 mr-2',
    right: 'left-full top-0 ml-2',
  };

  return (
    <div
      className={`absolute ${positionClasses[position]} z-[100] w-72 p-3 bg-popover border border-border rounded-lg shadow-xl text-sm pointer-events-none ${className}`}
    >
      {children}
      {/* Arrow pointer */}
      <div className={`absolute ${position === 'bottom' ? 'bottom-full left-6 mb-0' : position === 'top' ? 'top-full left-6 mt-0' : ''}`}>
        <div className="w-3 h-3 bg-popover border-l border-t border-border rotate-45"></div>
      </div>
    </div>
  );
}

