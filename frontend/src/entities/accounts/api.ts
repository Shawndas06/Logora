import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { accountsApi } from "~/shared/api";

export const useAccounts = () => {
  const queryClient = useQueryClient();

  const { data, isLoading, isSuccess, error } = useQuery({
    queryKey: ['accounts'],
    queryFn: accountsApi.getAccounts,
    retry: false,
  })

  return {
    data: data?.data || [],
    isLoading,
    isSuccess,
    error,
    refetch: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  }
}

export const useAccount = (id: string | undefined) => {
  const accounts = useAccounts();

  const account = accounts.data.find(acc => acc.id === Number(id));

  return account || null
}

export const useRemoveAccountMutation = () => {
  const queryClient = useQueryClient();

  const removeAccountMutation = useMutation({
    mutationFn: ({ accountId }: { accountId: number }) => accountsApi.deleteAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    }
  });

  return {
    remove: removeAccountMutation.mutate,
    isLoading: removeAccountMutation.isPending,
    error: removeAccountMutation.error,
    isSuccess: removeAccountMutation.isSuccess,
    data: removeAccountMutation.data,
  };
};

export const useUpdateAccountMutation = () => {
  const queryClient = useQueryClient();

  const updateAccountMutation = useMutation({
    mutationFn: ({ accountId, isActive }: { accountId: number, isActive: boolean }) => accountsApi.updateAccount(accountId, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
    },
  });

  return {
    update: updateAccountMutation.mutate,
    isLoading: updateAccountMutation.isPending,
    error: updateAccountMutation.error,
    isSuccess: updateAccountMutation.isSuccess,
    data: updateAccountMutation.data,
  };
}
