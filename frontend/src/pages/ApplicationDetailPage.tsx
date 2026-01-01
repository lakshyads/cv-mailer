import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { useApplicationMutations } from '@/hooks/useApplicationMutations';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { LoadingScreen } from '@/components/atoms/ui/Spinner';
import { ProgressTracker } from '@/components/organisms/shared/ProgressTracker';
import { Timeline } from '@/components/organisms/application/Timeline';
import { ApplicationHeader } from '@/components/organisms/application/ApplicationHeader';
import { ApplicationDetailsCard } from '@/components/organisms/application/ApplicationDetailsCard';
import { ConversationsCard } from '@/components/organisms/application/ConversationsCard';
import { RecruitersCard } from '@/components/organisms/application/RecruitersCard';
import { ApplicationActionsCard } from '@/components/organisms/application/ApplicationActionsCard';
import { EmailViewerModal } from '@/components/organisms/application/EmailViewerModal';
import { ConversationDetailModal } from '@/components/organisms/application/ConversationDetailModal';
import { toast } from 'sonner';
import type { EmailRecord, ConversationThread } from '@/types';

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [viewingEmail, setViewingEmail] = useState<EmailRecord | null>(null);
  const [viewingConversation, setViewingConversation] = useState<ConversationThread | null>(null);
  const [sendingFollowUpForRecruiters, setSendingFollowUpForRecruiters] = useState<Set<number>>(new Set());

  const { data: application, isLoading } = useQuery({
    queryKey: ['application', id],
    queryFn: () => applicationsApi.get(Number(id)),
    enabled: !!id,
  });

  const { data: conversationsData, isLoading: isLoadingConversations } = useQuery({
    queryKey: ['application', id, 'conversations'],
    queryFn: () => applicationsApi.getConversations(Number(id)),
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

  const handleTriggerFollowUp = (recruiterIds?: number[]) => {
    if (id) {
      // Track which recruiters are being sent to
      const recruiterSet = new Set(recruiterIds || []);
      setSendingFollowUpForRecruiters(recruiterSet);
      
      triggerFollowUp.mutate(
        { id: Number(id), recruiterIds },
        {
          onSettled: () => {
            // Clear the sending state after mutation completes
            setSendingFollowUpForRecruiters(new Set());
          },
        }
      );
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

  const conversations = conversationsData?.conversations || [];

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

            <ConversationsCard
              conversations={conversations}
              onViewEmail={setViewingEmail}
              onViewConversation={setViewingConversation}
              onSendFollowUp={handleTriggerFollowUp}
              sendingFollowUpForRecruiters={sendingFollowUpForRecruiters}
              isLoading={isLoadingConversations}
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
      <ConversationDetailModal
        conversation={viewingConversation}
        isOpen={!!viewingConversation}
        onClose={() => setViewingConversation(null)}
        onViewEmail={setViewingEmail}
        onSendFollowUp={handleTriggerFollowUp}
        isSendingFollowUp={
          viewingConversation?.recipient_id !== undefined &&
          sendingFollowUpForRecruiters.has(viewingConversation.recipient_id)
        }
      />
    </div>
  );
}

