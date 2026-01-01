import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { Spinner } from '@/components/atoms/ui/Spinner';
import { MessageSquare, Send, Mail } from 'lucide-react';
import { ConversationView } from './ConversationView';
import type { ConversationThread, EmailRecord } from '@/types';

interface ConversationsCardProps {
  conversations: ConversationThread[];
  onViewEmail: (email: EmailRecord) => void;
  onViewConversation?: (conversation: ConversationThread) => void;
  onSendFollowUp?: (recruiterIds?: number[]) => void;
  sendingFollowUpForRecruiters?: Set<number>;
  isLoading?: boolean;
}

/**
 * Conversations card component.
 * Displays all email conversations grouped by recruiter.
 */
export function ConversationsCard({
  conversations,
  onViewEmail,
  onViewConversation,
  onSendFollowUp,
  sendingFollowUpForRecruiters = new Set(),
  isLoading = false,
}: ConversationsCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Conversations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <Spinner />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Conversations</CardTitle>
          <span className="text-sm text-muted-foreground">
            {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        {conversations.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No conversations yet.</p>
            <p className="text-sm mt-2">Send your first contact email to start a conversation.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {conversations.map((conversation) => (
              <ConversationView
                key={conversation.recipient_email}
                conversation={conversation}
                onViewEmail={onViewEmail}
                onViewConversation={onViewConversation}
                onSendFollowUp={onSendFollowUp}
                isSendingFollowUp={
                  conversation.recipient_id !== undefined &&
                  sendingFollowUpForRecruiters.has(conversation.recipient_id)
                }
              />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

