import { useQuery, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "~/shared/api";

export const useUserTasks = (userId: number | undefined) => {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', userId],
    queryFn: () => tasksApi.getUserTasks(userId!),
    retry: false,
    enabled: !!userId,
  });

  return {
    data: data?.data || null,
    isLoading,
    error,
    refetch: () => queryClient.invalidateQueries({ 
      queryKey: ['tasks', userId] 
    }),
  };
};
