import { TimelineEvent } from '@/types';
import { formatDateTime } from '@/lib/utils';
import { Mail, Send, CheckCircle, Clock } from 'lucide-react';

interface TimelineProps {
  events: TimelineEvent[];
  className?: string;
}

const EVENT_ICONS = {
  first_contact: Mail,
  follow_up: Send,
  email_sent: Mail,
  status_change: CheckCircle,
};

const EVENT_COLORS = {
  first_contact: 'text-blue-600 dark:text-blue-400',
  follow_up: 'text-purple-600 dark:text-purple-400',
  email_sent: 'text-blue-600 dark:text-blue-400',
  status_change: 'text-green-600 dark:text-green-400',
};

export function Timeline({ events, className = '' }: TimelineProps) {
  if (events.length === 0) {
    return (
      <div className={`text-center py-8 text-muted-foreground ${className}`}>
        <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No timeline events yet.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {events.map((event, index) => {
        const Icon = EVENT_ICONS[event.type] || Clock;
        const colorClass = EVENT_COLORS[event.type] || 'text-muted-foreground';
        
        return (
          <div key={event.id} className="relative flex gap-4">
            {/* Timeline line */}
            {index < events.length - 1 && (
              <div className="absolute left-4 top-10 w-0.5 h-full bg-border" />
            )}
            
            {/* Icon */}
            <div className={`relative z-10 flex-shrink-0 w-8 h-8 rounded-full bg-background border-2 border-border flex items-center justify-center ${colorClass}`}>
              <Icon className="h-4 w-4" />
            </div>
            
            {/* Content */}
            <div className="flex-1 min-w-0 pb-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-sm">{event.title}</h4>
                  {event.description && (
                    <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                  )}
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {formatDateTime(event.timestamp)}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

