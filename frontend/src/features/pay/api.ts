import { useMutation, useQueryClient } from '@tanstack/react-query';
import { paymentApi } from '~/shared/api';

export const usePayMutation = () => {
  const queryClient = useQueryClient();

  const payMutation = useMutation({
    mutationFn: ({
      accountId,
      billingIds,
      amount,
      creditCard,
    }: {
      accountId: number;
      billingIds: number[];
      amount: number;
      creditCard?: { cardNumber: string };
    }) => paymentApi.pay(accountId, billingIds, amount, creditCard),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billings'] });
    },
  });

  return {
    pay: payMutation.mutate,
    reset: payMutation.reset,
    isLoading: payMutation.isPending,
    error: payMutation.error,
    isSuccess: payMutation.isSuccess,
  };
};
