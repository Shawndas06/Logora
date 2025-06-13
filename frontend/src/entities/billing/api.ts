import { useQuery, useQueryClient } from "@tanstack/react-query";
import { billingsApi } from "~/shared/api";

export const useBillings = (accountId: string | undefined, period: number) => {
  const queryClient = useQueryClient();

  const { data, isLoading, isSuccess, error } = useQuery({
    queryKey: ['billings', accountId, period],
    queryFn: () => billingsApi.getBillings(accountId!, period),
    retry: false,
    enabled: !!accountId,
  });

  console.log("D", data, error);

  return {
    data: data?.data || null,
    isLoading,
    isSuccess,
    error,
    refetch: () => queryClient.invalidateQueries({ 
      queryKey: ['billings', accountId, period] 
    }),
  };
};
