import { notifications } from '@mantine/notifications';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi } from '~/shared/api';

export const useSignInMutation = () => {
  const queryClient = useQueryClient();

  const signInMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.signIn(email, password),
    onSuccess: ({ data }) => {
      queryClient.setQueryData(['auth', 'me'], { success: true, data });
    },
    onError: () => {
      notifications.show({
        title: 'Ошибка входа',
        message: 'Неверный email или пароль.',
        color: 'red',
      });
    },
  });

  return {
    reset: signInMutation.reset,
    signIn: signInMutation.mutate,
    isLoading: signInMutation.isPending,
    error: signInMutation.error,
    isSuccess: signInMutation.isSuccess,
    data: signInMutation.data,
  };
};

export const useSignUpMutation = () => {
  const signUpMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.signUp(email, password),
    onSuccess: () => {
      notifications.show({
        title: 'Регистрация успешна',
        message: 'Вы можете войти в систему, используя свои учетные данные.',
      });
    },
    onError: () => {
      notifications.show({
        title: 'Ошибка регистрации',
        message: 'Пожалуйста, проверьте введенные данные и попробуйте снова.',
        color: 'red',
      });
    },
  });

  return {
    reset: signUpMutation.reset,
    signUp: signUpMutation.mutate,
    isLoading: signUpMutation.isPending,
    error: signUpMutation.error,
    isSuccess: signUpMutation.isSuccess,
    data: signUpMutation.data,
  };
};

export const useLogoutMutation = () => {
  const queryClient = useQueryClient();

  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      queryClient.setQueryData(['auth', 'me'], null);
      queryClient.clear();
    },
  });

  return {
    logout: logoutMutation.mutate,
    isLoading: logoutMutation.isPending,
    error: logoutMutation.error,
  };
};

