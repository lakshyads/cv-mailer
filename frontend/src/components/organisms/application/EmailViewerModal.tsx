import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { X } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';
import type { EmailRecord } from '@/types';

interface EmailViewerModalProps {
  email: EmailRecord | null;
  onClose: () => void;
}

/**
 * Email viewer modal component.
 * Displays full email content in a modal overlay.
 */
export function EmailViewerModal({ email, onClose }: EmailViewerModalProps) {
  if (!email) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle>{email.subject || ''}</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="text-sm text-muted-foreground mt-2">
            <p>
              To: {email.recipient_name || ''} ({email.recipient_email || ''})
            </p>
            <p>Sent: {email.sent_at ? formatDateTime(email.sent_at) : 'N/A'}</p>
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-auto">
          {email.body && (
            <div
              className="prose prose-sm max-w-none dark:prose-invert"
              dangerouslySetInnerHTML={{ __html: email.body }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

