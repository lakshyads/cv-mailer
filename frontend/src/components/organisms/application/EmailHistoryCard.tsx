import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { Spinner } from '@/components/atoms/ui/Spinner';
import { EmailStatusBadge } from '@/components/atoms/EmailStatusBadge';
import { Mail, Eye, Send } from 'lucide-react';
import { formatDateTime, capitalizeFirst } from '@/lib/utils';
import type { EmailRecord } from '@/types';

interface EmailHistoryCardProps {
  emails: EmailRecord[];
  onViewEmail: (email: EmailRecord) => void;
  onTriggerReachOut: () => void;
  isTriggerReachOutPending: boolean;
}

/**
 * Email history card component.
 * Displays list of emails sent for an application.
 */
export function EmailHistoryCard({
  emails,
  onViewEmail,
  onTriggerReachOut,
  isTriggerReachOutPending,
}: EmailHistoryCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Email History</CardTitle>
          <span className="text-sm text-muted-foreground">
            {emails.length} email{emails.length !== 1 ? 's' : ''}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        {emails.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No emails sent yet.</p>
            <div className="mt-4 flex gap-2 justify-center">
              <Button
                size="sm"
                onClick={onTriggerReachOut}
                disabled={isTriggerReachOutPending}
              >
                {isTriggerReachOutPending ? (
                  <>
                    <Spinner size="sm" className="mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Send First Contact
                  </>
                )}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {emails.map((email) => (
              <div key={email.id} className="border rounded-xl p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start gap-2 mb-2">
                      <Mail className="h-4 w-4 text-muted-foreground mt-1 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold truncate">{email.subject}</p>
                        <p className="text-sm text-muted-foreground mt-1">
                          To: {email.recipient_name}
                          <span className="text-xs ml-1">({email.recipient_email})</span>
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground ml-6">
                      <span>{capitalizeFirst(email.email_type.replace('_', ' '))}</span>
                      {email.is_follow_up && (
                        <span className="text-primary font-medium">Follow-up #{email.follow_up_number}</span>
                      )}
                      <span>{formatDateTime(email.sent_at)}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {email.body && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onViewEmail(email)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}
                    <EmailStatusBadge status={email.status} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

