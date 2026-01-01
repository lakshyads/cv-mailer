import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { EmailStatusBadge } from '@/components/atoms/EmailStatusBadge';
import { Mail, Eye, ChevronDown, ChevronUp, MessageSquare, Maximize2 } from 'lucide-react';
import { formatDateTime, capitalizeFirst } from '@/lib/utils';
import { useState } from 'react';
import type { ConversationThread, EmailRecord } from '@/types';

interface ConversationViewProps {
  conversation: ConversationThread;
  onViewEmail: (email: EmailRecord) => void;
  onViewConversation?: (conversation: ConversationThread) => void;
  onSendFollowUp?: (recruiterIds?: number[]) => void;
  isSendingFollowUp?: boolean;
}

/**
 * Conversation view component.
 * Displays a threaded email conversation for a single recruiter.
 */
export function ConversationView({
  conversation,
  onViewEmail,
  onViewConversation,
  onSendFollowUp,
  isSendingFollowUp = false,
}: ConversationViewProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const recipientDisplay = conversation.recipient_name || conversation.recipient_email;
  const recipientEmail = conversation.recipient_email;

  return (
    <Card className="border-l-4 border-l-primary">
      <CardHeader
        className="pb-3 cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <MessageSquare className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">{recipientDisplay}</CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">{recipientEmail}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs font-medium">
              <MessageSquare className="h-3 w-3" />
              <span>{conversation.message_count}</span>
            </div>
            {onViewConversation && (
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onViewConversation(conversation);
                }}
                className="h-8 w-8 p-0"
                title="View full conversation"
              >
                <Maximize2 className="h-4 w-4" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="h-8 w-8 p-0"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      {isExpanded && (
        <CardContent className="pt-0">
          <div className="space-y-3">
            {conversation.emails.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground text-sm">
                <Mail className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No emails in this conversation yet.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {conversation.emails.map((email, index) => (
                  <div
                    key={email.id}
                    className={`border rounded-lg p-3 transition-all ${index === conversation.emails.length - 1
                      ? 'bg-primary/5 border-primary/20'
                      : 'bg-muted/30'
                      }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start gap-2 mb-2">
                          {email.in_reply_to && (
                            <div className="mt-1.5 w-0.5 h-4 bg-primary/30 rounded-full flex-shrink-0" />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{email.subject}</p>
                            <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground mt-1">
                              <span>{capitalizeFirst(email.email_type.replace('_', ' '))}</span>
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
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {email.body && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onViewEmail(email)}
                            className="h-8 w-8 p-0"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </Button>
                        )}
                        <EmailStatusBadge status={email.status} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {onSendFollowUp && conversation.recipient_id !== undefined && (
              <div className="pt-2 border-t">
                <Button
                  variant="outline"
                  size="sm"
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
                      <Mail className="h-3.5 w-3.5 mr-2 animate-pulse" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="h-3.5 w-3.5 mr-2" />
                      Send Follow-up to {conversation.recipient_name || 'Recruiter'}
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

