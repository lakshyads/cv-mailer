import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { Spinner } from '@/components/atoms/ui/Spinner';
import { Send, Mail } from 'lucide-react';
import { getValidNextStatuses } from '@/lib/statusTransitions';
import { RecruiterSelectionDialog } from './RecruiterSelectionDialog';
import type { Application, JobStatus } from '@/types';

interface ApplicationActionsCardProps {
  application: Application;
  selectedStatus: string;
  notes: string;
  onStatusChange: (status: string) => void;
  onNotesChange: (notes: string) => void;
  onTriggerReachOut: () => void;
  onTriggerFollowUp: (recruiterIds?: number[]) => void;
  onUpdateStatus: () => void;
  isTriggerReachOutPending: boolean;
  isTriggerFollowUpPending: boolean;
  isUpdateStatusPending: boolean;
}

/**
 * Application actions card component.
 * Provides buttons for triggering reach-out, follow-up, and status updates.
 */
export function ApplicationActionsCard({
  application,
  selectedStatus,
  notes,
  onStatusChange,
  onNotesChange,
  onTriggerReachOut,
  onTriggerFollowUp,
  onUpdateStatus,
  isTriggerReachOutPending,
  isTriggerFollowUpPending,
  isUpdateStatusPending,
}: ApplicationActionsCardProps) {
  const [showRecruiterDialog, setShowRecruiterDialog] = useState(false);
  const validNextStatuses = getValidNextStatuses(application.status);
  const hasMultipleRecruiters = application.recruiters && application.recruiters.length > 1;

  const handleTriggerFollowUpClick = () => {
    if (hasMultipleRecruiters) {
      setShowRecruiterDialog(true);
    } else {
      // Single recruiter or no recruiters - send to all
      onTriggerFollowUp();
    }
  };

  const handleRecruiterSelection = (recruiterIds: number[]) => {
    if (recruiterIds.length === 0) {
      // Send to all if none selected
      onTriggerFollowUp();
    } else {
      onTriggerFollowUp(recruiterIds);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button
          onClick={onTriggerReachOut}
          disabled={isTriggerReachOutPending}
          className="w-full"
          variant="outline"
        >
          {isTriggerReachOutPending ? (
            <>
              <Spinner size="sm" className="mr-2" />
              Sending...
            </>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              Trigger Reach-out
            </>
          )}
        </Button>

        <Button
          onClick={handleTriggerFollowUpClick}
          disabled={isTriggerFollowUpPending}
          className="w-full"
          variant="outline"
        >
          {isTriggerFollowUpPending ? (
            <>
              <Spinner size="sm" className="mr-2" />
              Sending...
            </>
          ) : (
            <>
              <Mail className="h-4 w-4 mr-2" />
              Send Follow-up
              {hasMultipleRecruiters && (
                <span className="ml-1 text-xs opacity-75">(Select)</span>
              )}
            </>
          )}
        </Button>

        {showRecruiterDialog && application.recruiters && (
          <RecruiterSelectionDialog
            recruiters={application.recruiters}
            isOpen={showRecruiterDialog}
            onClose={() => setShowRecruiterDialog(false)}
            onConfirm={handleRecruiterSelection}
            title="Select Recruiters for Follow-up"
            confirmLabel="Send Follow-up"
          />
        )}

        <div className="border-t pt-4">
          <label className="text-sm font-medium">Update Status</label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            disabled={isUpdateStatusPending}
          >
            <option value="">Select status...</option>
            {validNextStatuses.length === 0 ? (
              <option value="" disabled>
                No valid status transitions (terminal state)
              </option>
            ) : (
              validNextStatuses.map((status) => (
                <option key={status} value={status}>
                  {status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))
            )}
          </select>
          {validNextStatuses.length === 0 && (
            <p className="mt-1 text-xs text-muted-foreground">
              This application is in a terminal state and cannot be changed.
            </p>
          )}
        </div>

        <div>
          <label className="text-sm font-medium">Notes (optional)</label>
          <textarea
            value={notes}
            onChange={(e) => onNotesChange(e.target.value)}
            placeholder="Add any notes..."
            rows={3}
            className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </div>

        <Button
          onClick={onUpdateStatus}
          disabled={!selectedStatus || isUpdateStatusPending}
          className="w-full"
        >
          {isUpdateStatusPending ? (
            <>
              <Spinner size="sm" className="mr-2" />
              Updating...
            </>
          ) : (
            'Update Status'
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

