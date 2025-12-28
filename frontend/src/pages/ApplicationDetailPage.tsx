import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { useApplicationMutations } from '@/hooks/useApplicationMutations';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { LoadingScreen } from '@/components/ui/Spinner';
import { ProgressTracker } from '@/components/ProgressTracker';
import { Timeline } from '@/components/Timeline';
import { ApplicationHeader } from '@/components/application/ApplicationHeader';
import { ApplicationDetailsCard } from '@/components/application/ApplicationDetailsCard';
import { EmailHistoryCard } from '@/components/application/EmailHistoryCard';
import { RecruitersCard } from '@/components/application/RecruitersCard';
import { ApplicationActionsCard } from '@/components/application/ApplicationActionsCard';
import { EmailViewerModal } from '@/components/application/EmailViewerModal';
import { toast } from 'sonner';
import type { EmailRecord } from '@/types';

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [viewingEmail, setViewingEmail] = useState<EmailRecord | null>(null);

  const { data: application, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: () => applicationsApi.get(Number(id)),
    enabled: !!id,
  });

  const { data: emailsData } = useQuery({
    queryKey: ['application', id, 'emails'],
    queryFn: () => applicationsApi.getEmails(Number(id)),
    enabled: !!id,
  });

  const { data: timelineData } = useQuery({
    queryKey: ['application', id, 'timeline'],
    queryFn: () => applicationsApi.getTimeline(Number(id)),
    enabled: !!id,
  });

  const { triggerReachOut, triggerFollowUp, updateStatus } = useApplicationMutations();

  const handleTriggerReachOut = () => {
    if (id) {
      triggerReachOut.mutate(Number(id));
    }
  };

  const handleTriggerFollowUp = () => {
    if (id) {
      triggerFollowUp.mutate(Number(id));
    }
  };

  const handleUpdateStatus = () => {
    if (!selectedStatus || !id) {
      toast.error('Please select a status');
      return;
    }
    updateStatus.mutate({ id: Number(id), status: selectedStatus, notes: notes || undefined }, {
      onSuccess: () => {
        setSelectedStatus('');
        setNotes('');
      },
    });
  };

  if (isLoading || !application) {
    return <LoadingScreen />;
  }

  const emails = emailsData?.emails || [];

  return (
    <div className="space-y-6">
      <ApplicationHeader application={application} />

      {/* Progress Tracker */}
      <Card>
        <CardContent className="pt-6">
          <ProgressTracker
            currentStatus={application.status}
            lastMainFlowStatus={application.last_main_flow_status}
          />
        </CardContent>
      </Card>

      {/* Main Content */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <ApplicationDetailsCard application={application} />

          {/* Timeline and Email History */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <Timeline events={timelineData?.events || []} />
              </CardContent>
            </Card>

            <EmailHistoryCard
              emails={emails}
              onViewEmail={setViewingEmail}
              onTriggerReachOut={handleTriggerReachOut}
              isTriggerReachOutPending={triggerReachOut.isPending}
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <RecruitersCard recruiters={application.recruiters} />

          <ApplicationActionsCard
            application={application}
            selectedStatus={selectedStatus}
            notes={notes}
            onStatusChange={setSelectedStatus}
            onNotesChange={setNotes}
            onTriggerReachOut={handleTriggerReachOut}
            onTriggerFollowUp={handleTriggerFollowUp}
            onUpdateStatus={handleUpdateStatus}
            isTriggerReachOutPending={triggerReachOut.isPending}
            isTriggerFollowUpPending={triggerFollowUp.isPending}
            isUpdateStatusPending={updateStatus.isPending}
          />
        </div>
      </div>

      <EmailViewerModal email={viewingEmail} onClose={() => setViewingEmail(null)} />
    </div>
  );
}

