import { useMutation, useQueryClient } from '@tanstack/react-query';
import { syncApi } from '@/api/client';
import { Card, CardContent } from '@/components/atoms/ui/Card';
import { Button } from '@/components/atoms/ui/Button';
import { RefreshCw, Send, Eye } from 'lucide-react';
import { toast } from 'sonner';

/**
 * Google Sheets Sync Controls Component
 * 
 * Reusable component for syncing applications from Google Sheets and sending follow-ups.
 * Handles all sync-related mutations and UI.
 */
export function GoogleSheetsSync() {
  const queryClient = useQueryClient();

  // Sync applications mutation
  const syncApplicationsMutation = useMutation({
    mutationFn: (dryRun: boolean) => syncApi.syncApplications(dryRun),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      toast.success(data.message || 'Applications synced successfully');
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to sync applications');
    },
  });

  // Send follow-ups mutation
  const sendFollowUpsMutation = useMutation({
    mutationFn: (dryRun: boolean) => syncApi.sendFollowUps(dryRun),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      toast.success(data.message || 'Follow-ups sent successfully');
    },
    onError: (error: unknown) => {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to send follow-ups');
    },
  });

  return (
    <Card>
      <CardContent className="py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h3 className="text-lg font-semibold whitespace-nowrap">Google Sheets Sync</h3>
          <div className="flex flex-wrap gap-2">
            {/* Send Follow-ups */}
            <Button
              onClick={() => sendFollowUpsMutation.mutate(false)}
              disabled={sendFollowUpsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
              size="sm"
            >
              <Send className={`h-4 w-4 ${sendFollowUpsMutation.isPending ? 'animate-spin' : ''}`} />
              Send Follow-ups
            </Button>
            {/* Dry Run Follow-ups */}
            <Button
              onClick={() => sendFollowUpsMutation.mutate(true)}
              disabled={sendFollowUpsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
              size="sm"
            >
              <Eye className="h-4 w-4" />
              Dry Run Follow-ups
            </Button>
            {/* Sync Applications */}
            <Button
              onClick={() => syncApplicationsMutation.mutate(false)}
              disabled={syncApplicationsMutation.isPending}
              variant="outline"
              className="flex items-center gap-2"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 ${syncApplicationsMutation.isPending ? 'animate-spin' : ''}`} />
              Sync Applications & Reach Out
            </Button>
            {/* Dry Run Sync Applications */}
            <Button
              onClick={() => syncApplicationsMutation.mutate(true)}
              disabled={syncApplicationsMutation.isPending}
              variant="default"
              className="flex items-center gap-2"
              size="sm"
            >
              <Eye className="h-4 w-4" />
              Sync Applications
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

