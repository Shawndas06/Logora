import { useQuery } from "@tanstack/react-query";
import { authApi } from "../api";

export const useAuth = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authApi.getCurrentUser,
    retry: false,
    refetchOnMount: false,
  });

  return {
    user: data?.data || null,
    isLoading,
    isAuthenticated: !!data?.data && !error,
  };
};
