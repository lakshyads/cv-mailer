import { useMutation, useQueryClient } from '@tanstack/react-query';
import { applicationsApi } from '@/api/client';
import { toast } from 'sonner';
import { extractErrorMessage } from '@/lib/errorHandling';

/**
 * Custom hook for application-related mutations.
 * Provides consistent error handling and query invalidation.
 */
export function useApplicationMutations() {
  const queryClient = useQueryClient();

  const triggerReachOut = useMutation({
    mutationFn: (id: number) => applicationsApi.triggerReachOut(id),
    onSuccess: (data, id) => {
      // Convert id to string to match query key format from useParams
      const idString = String(id);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'conversations'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'timeline'] });
      toast.success(data.message || 'Reach-out email sent successfully');
    },
    onError: (error: unknown) => {
      toast.error(extractErrorMessage(error, 'Failed to send reach-out email'));
    },
  });

  const triggerFollowUp = useMutation({
    mutationFn: ({ id, recruiterIds }: { id: number; recruiterIds?: number[] }) =>
      applicationsApi.triggerFollowUp(id, undefined, recruiterIds),
    onSuccess: (data, variables) => {
      // Convert id to string to match query key format from useParams
      const idString = String(variables.id);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'conversations'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'timeline'] });
      toast.success(data.message || 'Follow-up email sent successfully');
    },
    onError: (error: unknown) => {
      toast.error(extractErrorMessage(error, 'Failed to send follow-up email'));
    },
  });

  const updateStatus = useMutation({
    mutationFn: ({ id, status, notes }: { id: number; status: string; notes?: string }) =>
      applicationsApi.updateStatus(id, status, notes),
    onSuccess: (_data, variables) => {
      // Invalidate all related queries to ensure UI updates
      // Convert id to string to match query key format from useParams
      const idString = String(variables.id);
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'timeline'] });
      queryClient.invalidateQueries({ queryKey: ['application', idString, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['statistics'] });
      toast.success('Status updated successfully');
    },
    onError: (error: unknown) => {
      const errorMessage = extractErrorMessage(error, 'Failed to update status');
      toast.error(errorMessage);
    },
  });

  return {
    triggerReachOut,
    triggerFollowUp,
    updateStatus,
  };
}

