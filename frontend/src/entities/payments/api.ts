import { useQuery, useQueryClient } from "@tanstack/react-query";
import { paymentApi } from "~/shared/api";

export const usePayments = (accountId: string | undefined) => {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['payments', accountId],
    queryFn: () => paymentApi.paymentHistory(accountId!),
    retry: false,
    enabled: !!accountId,
  });

  return {
    data: data?.data || null,
    isLoading,
    error,
    refetch: () => queryClient.invalidateQueries({ 
      queryKey: ['payments', accountId] 
    }),
  };
};
