import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { EmailStatusBadge } from '@/components/atoms/EmailStatusBadge';
import { X, Eye, Mail, MessageSquare } from 'lucide-react';
import { formatDateTime, capitalizeFirst } from '@/lib/utils';
import type { ConversationThread, EmailRecord } from '@/types';

interface ConversationDetailModalProps {
  conversation: ConversationThread | null;
  isOpen: boolean;
  onClose: () => void;
  onViewEmail: (email: EmailRecord) => void;
  onSendFollowUp?: (recruiterIds?: number[]) => void;
  isSendingFollowUp?: boolean;
}

/**
 * Conversation detail modal component.
 * Displays full conversation thread in a modal overlay.
 */
export function ConversationDetailModal({
  conversation,
  isOpen,
  onClose,
  onViewEmail,
  onSendFollowUp,
  isSendingFollowUp = false,
}: ConversationDetailModalProps) {
  if (!isOpen || !conversation) return null;

  const recipientDisplay = conversation.recipient_name || conversation.recipient_email;
  const recipientEmail = conversation.recipient_email;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="flex-shrink-0 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <MessageSquare className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">{recipientDisplay}</CardTitle>
                <p className="text-sm text-muted-foreground mt-0.5">{recipientEmail}</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="mt-3 flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs font-medium">
              <MessageSquare className="h-3 w-3" />
              <span>{conversation.message_count}</span>
            </div>
            {conversation.thread_id && (
              <span className="text-xs">Thread ID: {conversation.thread_id}</span>
            )}
            {conversation.last_activity && (
              <span>Last activity: {formatDateTime(conversation.last_activity)}</span>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pt-6">
          {conversation.emails.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No emails in this conversation yet.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {conversation.emails.map((email, index) => (
                <div
                  key={email.id}
                  className={`border rounded-lg p-4 transition-all ${index === conversation.emails.length - 1
                    ? 'bg-primary/5 border-primary/30 shadow-sm'
                    : 'bg-muted/30'
                    }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-3">
                        {email.in_reply_to && (
                          <div className="mt-2 flex flex-col items-center">
                            <div className="w-0.5 h-6 bg-primary/40 rounded-full" />
                            <div className="w-2 h-2 rounded-full bg-primary/40 mt-1" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-base">{email.subject}</h3>
                            {email.in_reply_to && (
                              <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded">
                                Reply
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground mb-3">
                            <span className="font-medium">
                              {capitalizeFirst(email.email_type.replace('_', ' '))}
                            </span>
                            {email.is_follow_up && (
                              <span className="text-primary font-medium">
                                Follow-up #{email.follow_up_number}
                              </span>
                            )}
                            {email.thread_id && (
                              <span className="text-xs opacity-75">Threaded</span>
                            )}
                            <span>{formatDateTime(email.sent_at || email.created_at)}</span>
                          </div>
                          {email.body && (
                            <div className="mt-3">
                              <div
                                className="prose prose-sm max-w-none dark:prose-invert text-sm"
                                dangerouslySetInnerHTML={{ __html: email.body }}
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-2 flex-shrink-0">
                      <EmailStatusBadge status={email.status} />
                      {email.body && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onViewEmail(email)}
                          className="mt-2"
                        >
                          <Eye className="h-3.5 w-3.5 mr-2" />
                          View Full
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {onSendFollowUp && conversation.recipient_id !== undefined && (
            <div className="mt-6 pt-6 border-t">
              <Button
                variant="default"
                size="lg"
                onClick={() => {
                  if (conversation.recipient_id !== undefined) {
                    onSendFollowUp([conversation.recipient_id]);
                  }
                }}
                disabled={isSendingFollowUp}
                className="w-full"
              >
                {isSendingFollowUp ? (
                  <>
                    <Mail className="h-4 w-4 mr-2 animate-pulse" />
                    Sending Follow-up...
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4 mr-2" />
                    Send Follow-up to {conversation.recipient_name || 'Recruiter'}
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

