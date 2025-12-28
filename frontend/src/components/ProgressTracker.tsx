import { JobStatus } from '@/types';

interface ProgressTrackerProps {
  currentStatus: JobStatus;
  className?: string;
  lastMainFlowStatus?: JobStatus; // Last status in main flow before terminal state
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
const TERMINAL_STATES: JobStatus[] = ['rejected', 'ghosted', 'withdrawn', 'offer_rejected'];

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
  offer_rejected: 'Offer Rejected',
  draft: 'Draft', // Legacy, not used in main flow
};

export function ProgressTracker({ currentStatus, className = '', lastMainFlowStatus }: ProgressTrackerProps) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);
  const isTerminal = TERMINAL_STATES.includes(currentStatus);
  const isAccepted = currentStatus === 'accepted';
  const isOfferRejected = currentStatus === 'offer_rejected';
  const isApplicationWithdrawn = currentStatus === 'withdrawn';
  const isInMainFlow = currentIndex >= 0;

  // For terminal states, determine which stages were completed
  let completedUpToIndex = -1;
  if (isOfferRejected) {
    // offer_rejected can only come from offer_received, so show all stages up to offer_received
    completedUpToIndex = STATUS_ORDER.indexOf('offer_received');
  } else if (isTerminal) {
    if (lastMainFlowStatus && STATUS_ORDER.includes(lastMainFlowStatus)) {
      // Use provided last main flow status
      completedUpToIndex = STATUS_ORDER.indexOf(lastMainFlowStatus);
    } else {
      // Infer: terminal states can only be reached from reached_out or later
      // Default to reached_out (minimum stage for terminal states)
      completedUpToIndex = STATUS_ORDER.indexOf('reached_out');
    }
  } else if (isAccepted) {
    // Accepted means all stages completed
    completedUpToIndex = STATUS_ORDER.length - 1;
  } else if (isInMainFlow) {
    // Current status is in main flow
    completedUpToIndex = currentIndex;
  }

  const totalStages = STATUS_ORDER.length;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
        <span>Application Progress</span>
        <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
      </div>
      <div className="relative">
        {/* Progress line background - spans full width */}
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-muted" />

        {/* Progress line fill - calculated to reach center of last completed circle */}
        {completedUpToIndex >= 0 && (
          <div
            className={`absolute top-4 left-0 h-0.5 transition-all duration-300 ${isOfferRejected
              ? 'bg-orange-500'
              : isTerminal
                ? 'bg-red-500'
                : isAccepted
                  ? 'bg-green-500'
                  : 'bg-primary'
              }`}
            style={{
              // With justify-between: first at 0%, last at 100%, others evenly spaced
              // Circle centers are at: index / (total - 1) * 100%
              width: completedUpToIndex === totalStages - 1
                ? '100%'
                : `${(completedUpToIndex / (totalStages - 1)) * 100}%`,
            }}
          />
        )}

        {/* Status points - using justify-between for edge alignment */}
        <div className="relative flex justify-between items-start">
          {STATUS_ORDER.map((status, index) => {
            const isCompleted = index <= completedUpToIndex;
            const isCurrent = status === currentStatus && !isTerminal;

            // Determine colors based on state
            let bgColor = 'bg-background';
            let borderColor = 'border-muted';
            let textColor = 'text-muted-foreground';

            if (isCompleted) {
              if (isOfferRejected || isApplicationWithdrawn) {
                bgColor = 'bg-orange-500';
                borderColor = 'border-orange-500';
                textColor = 'text-white';
              } else if (isTerminal) {
                bgColor = 'bg-red-500';
                borderColor = 'border-red-500';
                textColor = 'text-white';
              } else if (isAccepted) {
                bgColor = 'bg-green-500';
                borderColor = 'border-green-500';
                textColor = 'text-white';
              } else {
                bgColor = 'bg-primary';
                borderColor = 'border-primary';
                textColor = 'text-primary-foreground';
              }
            }

            return (
              <div
                key={status}
                className="flex flex-col items-center relative z-10"
              >
                <div
                  className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-all ${isCurrent ? 'scale-110' : ''
                    } ${bgColor} ${borderColor} ${textColor}`}
                >
                  {isCompleted ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-xs font-medium">{index + 1}</span>
                  )}
                </div>
                <span
                  className={`mt-2 text-xs text-center max-w-[80px] ${isCurrent ? 'font-semibold text-foreground' : 'text-muted-foreground'
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
      {isOfferRejected && (
        <div className="mt-4 p-3 rounded-lg text-sm bg-orange-50 dark:bg-orange-900/20 text-orange-800 dark:text-orange-200">
          <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
          <span className="ml-2 text-xs">(Offer rejected)</span>
        </div>
      )}
      {isApplicationWithdrawn && (
        <div className="mt-4 p-3 rounded-lg text-sm bg-orange-50 dark:bg-orange-900/20 text-orange-800 dark:text-orange-200">
          <span className="font-medium">{STATUS_LABELS[currentStatus]}</span>
          <span className="ml-2 text-xs">(Application withdrawn)</span>
        </div>
      )}
      {isTerminal && !isOfferRejected && !isApplicationWithdrawn && (
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

