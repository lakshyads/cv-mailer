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
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'timeline'] });
      toast.success(data.message || 'Reach-out email sent successfully');
    },
    onError: (error: unknown) => {
      toast.error(extractErrorMessage(error, 'Failed to send reach-out email'));
    },
  });

  const triggerFollowUp = useMutation({
    mutationFn: (id: number) => applicationsApi.triggerFollowUp(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'emails'] });
      queryClient.invalidateQueries({ queryKey: ['application', id, 'timeline'] });
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
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['application', variables.id] });
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

