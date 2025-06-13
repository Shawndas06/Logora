import { useMutation, useQueryClient } from "@tanstack/react-query";
import { accountsApi, type CreateAccount } from "~/shared/api";

export const useCreateAccountMutation = () => {
  const queryClient = useQueryClient();

  const createAccountMutation = useMutation({
    mutationFn: ({ account }: { account: CreateAccount }) => accountsApi.createAccount(account),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
    }
  });

  return {
    create: createAccountMutation.mutate,
    isLoading: createAccountMutation.isPending,
    error: createAccountMutation.error,
    isSuccess: createAccountMutation.isSuccess,
    data: createAccountMutation.data,
  };
};
