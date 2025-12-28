import { JobStatus } from '@/types';

interface ProgressTrackerProps {
  currentStatus: JobStatus;
  className?: string;
}

// Main status flow (one-directional)
const STATUS_ORDER: JobStatus[] = [
  'applied',              // 1. Initial state - application already submitted
  'reached_out',          // 2. After sending first contact emails
  'interview_scheduled',  // 3. Interview scheduled
  'interview_in_progress', // 4. Interview in progress
  'result_awaited',       // 5. Waiting for result
  'offer_received',       // 6. Offer received
  'accepted',             // 7. Accepted (terminal - positive)
];

// Terminal states (not in main flow)
const TERMINAL_STATES: JobStatus[] = ['rejected', 'ghosted', 'withdrawn'];

const STATUS_LABELS: Record<JobStatus, string> = {
  applied: 'Applied',
  reached_out: 'Reached Out',
  interview_scheduled: 'Interview Scheduled',
  interview_in_progress: 'Interview In Progress',
  result_awaited: 'Result Awaited',
  offer_received: 'Offer Received',
  accepted: 'Accepted',
  rejected: 'Rejected',
  ghosted: 'Ghosted',
  withdrawn: 'Withdrawn',
  draft: 'Draft', // Legacy, not used in main flow
};

export function ProgressTracker({ currentStatus, className = '' }: ProgressTrackerProps) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);
  const isTerminal = TERMINAL_STATES.includes(currentStatus);
  const isAccepted = currentStatus === 'accepted';
  const isInMainFlow = currentIndex >= 0;

  // Calculate progress width
  let progressWidth = '0%';
  if (isTerminal || isAccepted) {
    // Terminal states show full progress (reached end, just different outcome)
    progressWidth = '100%';
  } else if (isInMainFlow) {
    // Show progress up to current step
    progressWidth = `${(currentIndex / (STATUS_ORDER.length - 1)) * 100}%`;
  }

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
          className={`absolute top-4 left-0 h-0.5 transition-all duration-300 ${
            isTerminal ? 'bg-red-500' : isAccepted ? 'bg-green-500' : 'bg-primary'
          }`}
          style={{ width: progressWidth }}
        />
        
        {/* Status points */}
        <div className="relative flex justify-between">
          {STATUS_ORDER.map((status, index) => {
            const isActive = index <= currentIndex && isInMainFlow;
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
      {isTerminal && (
        <div className="mt-4 p-3 rounded-lg text-sm bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200">
          <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
          <span className="ml-2 text-xs">(Terminal state - application closed)</span>
        </div>
      )}
      {isAccepted && (
        <div className="mt-4 p-3 rounded-lg text-sm bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200">
          <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
          <span className="ml-2 text-xs">(Application completed successfully)</span>
        </div>
      )}
    </div>
  );
}

