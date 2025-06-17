import { useQuery, useQueryClient } from "@tanstack/react-query";
import { paymentApi, type Payment } from "~/shared/api";

const mapPaymentData = (payments: Payment[]) => {
  return payments.map(payment => ({
    id: payment.id,
    amount: payment.amount,
    accountId: payment.account_id,
    createdAt: payment.created_at,
    billingPeriod: payment.billing_ids,
    status: payment.status,
  }));
};

export const usePayments = (accountId: string | undefined) => {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['payments', accountId],
    queryFn: () => paymentApi.paymentHistory(accountId!),
    retry: false,
    enabled: !!accountId,
  });

  return {
    data: data?.data ? mapPaymentData(data.data) : null,
    isLoading,
    error,
    refetch: () => queryClient.invalidateQueries({ 
      queryKey: ['payments', accountId] 
    }),
  };
};
