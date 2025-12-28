import { JobStatus } from '@/types';

interface ProgressTrackerProps {
  currentStatus: JobStatus;
  className?: string;
}

const STATUS_ORDER: JobStatus[] = [
  'draft',
  'reached_out',
  'applied',
  'interview_scheduled',
  'interview_in_progress',
  'result_awaited',
  'offer_received',
  'accepted',
];

const STATUS_LABELS: Record<JobStatus, string> = {
  draft: 'Draft',
  reached_out: 'Reached Out',
  applied: 'Applied',
  interview_scheduled: 'Interview Scheduled',
  interview_in_progress: 'Interview In Progress',
  result_awaited: 'Result Awaited',
  offer_received: 'Offer Received',
  rejected: 'Rejected',
  ghosted: 'Ghosted',
  accepted: 'Accepted',
  withdrawn: 'Withdrawn',
};

export function ProgressTracker({ currentStatus, className = '' }: ProgressTrackerProps) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);
  const isRejected = currentStatus === 'rejected' || currentStatus === 'ghosted' || currentStatus === 'withdrawn';
  const isAccepted = currentStatus === 'accepted';

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
        <span>Application Progress</span>
        <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
      </div>
      <div className="relative">
        {/* Progress line */}
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-muted" />
        <div
          className="absolute top-4 left-0 h-0.5 bg-primary transition-all duration-300"
          style={{
            width: isRejected || isAccepted
              ? '100%'
              : currentIndex >= 0
              ? `${(currentIndex / (STATUS_ORDER.length - 1)) * 100}%`
              : '0%',
          }}
        />
        
        {/* Status points */}
        <div className="relative flex justify-between">
          {STATUS_ORDER.map((status, index) => {
            const isActive = index <= currentIndex;
            const isCurrent = status === currentStatus;
            
            return (
              <div key={status} className="flex flex-col items-center" style={{ width: `${100 / (STATUS_ORDER.length - 1)}%` }}>
                <div
                  className={`relative z-10 w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${
                    isCurrent
                      ? 'bg-primary border-primary text-primary-foreground scale-110'
                      : isActive
                      ? 'bg-primary border-primary text-primary-foreground'
                      : 'bg-background border-muted text-muted-foreground'
                  }`}
                >
                  {isActive ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>
                <span
                  className={`mt-2 text-xs text-center max-w-[80px] ${
                    isCurrent ? 'font-semibold text-foreground' : 'text-muted-foreground'
                  }`}
                >
                  {STATUS_LABELS[status]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Terminal states */}
      {(isRejected || isAccepted) && (
        <div className={`mt-4 p-3 rounded-lg text-sm ${
          isAccepted ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200' : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
        }`}>
          <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
        </div>
      )}
    </div>
  );
}

