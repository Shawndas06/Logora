import { zodResolver } from '@hookform/resolvers/zod';
import {
  Anchor,
  Box,
  Button,
  Center,
  Divider,
  Group,
  Modal,
  Paper,
  PasswordInput,
  Select,
  Stack,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import {
  IconEye,
  IconEyeOff,
  IconGenderBigender,
  IconLock,
  IconLogin,
  IconMail,
  IconMan,
  IconUserPlus,
} from '@tabler/icons-react';
import { z } from 'zod';
import { ShowOnly } from '~/shared/ui/showOnly';

import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';

import { useSignInMutation, useSignUpMutation } from '../../api';
import { UserAvatar } from '../UserAvatar';

const loginSchema = z.object({
  email: z.string().min(1, 'Email обязателен').email('Неверный формат email'),
  password: z
    .string()
    .min(1, 'Пароль обязателен')
    .min(6, 'Пароль должен содержать минимум 6 символов'),
});

const registerSchema = z
  .object({
    email: z.string().min(1, 'Email обязателен').email('Неверный формат email'),
    name: z.string().min(1, 'Поле ФИО не может быть пустым'),
    description: z.string().optional(),
    sex: z.string().min(1, 'Поле должно быть заполнено'),
    password: z
      .string()
      .min(1, 'Пароль обязателен')
      .min(6, 'Пароль должен содержать минимум 6 символов')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        'Пароль должен содержать заглавную букву, строчную букву и цифру'
      ),
    confirmPassword: z.string().min(1, 'Подтверждение пароля обязательно'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Пароли не совпадают',
    path: ['confirmPassword'],
  });

type LoginFormData = z.infer<typeof loginSchema>;
type RegisterFormData = z.infer<typeof registerSchema>;

type AuthMode = 'login' | 'register';

export const AuthModal = () => {
  const [modalOpened, setModalOpened] = useState(false);
  const [mode, setMode] = useState<AuthMode>('login');

  const {
    signIn,
    isLoading: isSignInLoading,
    isSuccess: isSignInSuccess,
    reset: resetSignIn,
  } = useSignInMutation();

  const {
    signUp,
    isLoading: isSignUpLoading,
    isSuccess: isSignUpSuccess,
    reset: resetSignUp,
  } = useSignUpMutation();

  // Determine current loading and error states
  const isLoading = isSignInLoading || isSignUpLoading;
  const isSuccess = mode === 'login' ? isSignInSuccess : isSignUpSuccess;

  const {
    control: loginControl,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors },
    reset: resetLogin,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const {
    control: registerControl,
    handleSubmit: handleRegisterSubmit,
    formState: { errors: registerErrors },
    reset: resetRegister,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      name: '',
      sex: '',
      description: '',
    },
  });

  const handleLogin = (data: LoginFormData) => {
    signIn(
      { email: data.email, password: data.password },
      {
        onSuccess: () => {
          setModalOpened(false);
        },
      }
    );
  };

  const handleRegister = (data: RegisterFormData) => {
    signUp(
      {
        email: data.email,
        password: data.password,
        name: data.name,
        description: data.description ?? '',
        sex: Number.parseInt(data.sex),
      },
      {
        onSuccess: () => {
          setMode('login');
        },
      }
    );
  };

  const handleModeSwitch = (newMode: AuthMode) => {
    setMode(newMode);
    resetLogin();
    resetRegister();
  };

  const handleClose = () => {
    setMode('login');
    setModalOpened(false);
    resetLogin();
    resetRegister();
  };

  const getPasswordStrength = (password: string) => {
    let strength = 0;
    const checks = [
      password.length >= 6,
      /[a-z]/.test(password),
      /[A-Z]/.test(password),
      /\d/.test(password),
      /[^a-zA-Z\d]/.test(password),
    ];

    strength = checks.filter(Boolean).length;

    if (strength < 2) return { level: 'weak', color: 'red', text: 'Слабый' };
    if (strength < 4) return { level: 'medium', color: 'yellow', text: 'Средний' };
    return { level: 'strong', color: 'green', text: 'Сильный' };
  };

  return (
    <>
      <Modal
        opened={modalOpened}
        onClose={handleClose}
        title={
          <Group>
            {mode === 'login' ? <IconLogin size={20} /> : <IconUserPlus size={20} />}
            <Title order={3}>{mode === 'login' ? 'Вход в систему' : 'Регистрация'}</Title>
          </Group>
        }
        size="md"
        centered
        closeOnClickOutside={!isLoading}
        closeOnEscape={!isLoading}
      >
        <Stack gap="lg">
          <Paper withBorder p="xs" radius="md" bg="gray.0">
            <Group justify="center" gap="xs">
              <Button
                variant={mode === 'login' ? 'filled' : 'subtle'}
                size="sm"
                onClick={() => handleModeSwitch('login')}
                disabled={isLoading}
                leftSection={<IconLogin size={16} />}
              >
                Войти
              </Button>
              <Button
                variant={mode === 'register' ? 'filled' : 'subtle'}
                size="sm"
                onClick={() => handleModeSwitch('register')}
                disabled={isLoading}
                leftSection={<IconUserPlus size={16} />}
              >
                Зарегистрироваться
              </Button>
            </Group>
          </Paper>

          {mode === 'login' && (
            <Stack gap="md">
              <Title order={4} ta="center">
                Добро пожаловать!
              </Title>
              <Text size="sm" c="dimmed" ta="center">
                Войдите в свой аккаунт для доступа к лицевым счетам
              </Text>

              <Controller
                name="email"
                control={loginControl}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    label="Email"
                    placeholder="example@domain.com"
                    leftSection={<IconMail size={16} />}
                    error={loginErrors.email?.message}
                    disabled={isLoading}
                  />
                )}
              />

              <Controller
                name="password"
                control={loginControl}
                render={({ field }) => (
                  <PasswordInput
                    {...field}
                    label="Пароль"
                    placeholder="Введите пароль"
                    leftSection={<IconLock size={16} />}
                    error={loginErrors.password?.message}
                    disabled={isLoading}
                    visibilityToggleIcon={({ reveal }) =>
                      reveal ? <IconEyeOff size={16} /> : <IconEye size={16} />
                    }
                  />
                )}
              />

              <Group justify="flex-end">
                <Anchor size="sm" c="dimmed">
                  Забыли пароль?
                </Anchor>
              </Group>

              <Button
                size="lg"
                loading={isLoading}
                disabled={isLoading || isSuccess}
                onClick={handleLoginSubmit(handleLogin)}
                leftSection={<IconLogin size={16} />}
                fullWidth
              >
                {isLoading ? 'Проверка данных...' : 'Войти'}
              </Button>
            </Stack>
          )}
          {mode === 'register' && (
            <Stack gap="md">
              <Title order={4} ta="center">
                Создать аккаунт
              </Title>
              <Text size="sm" c="dimmed" ta="center">
                Зарегистрируйтесь для управления лицевыми счетами
              </Text>

              <Controller
                name="email"
                control={registerControl}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    label="Email"
                    placeholder="example@domain.com"
                    leftSection={<IconMail size={16} />}
                    error={registerErrors.email?.message}
                    disabled={isLoading}
                  />
                )}
              />

              <Controller
                name="name"
                control={registerControl}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    label="ФИО"
                    placeholder="Иванов Иван Иванович"
                    leftSection={<IconMan size={16} />}
                    error={registerErrors.name?.message}
                    disabled={isLoading}
                  />
                )}
              />

              <Controller
                name="sex"
                control={registerControl}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Пол"
                    placeholder="Выберите пол"
                    leftSection={<IconGenderBigender size={16} />}
                    data={[
                      { value: '1', label: 'Мужской' },
                      { value: '0', label: 'Женский' },
                    ]}
                    error={registerErrors.sex?.message}
                    disabled={isLoading}
                  />
                )}
              />

              <Controller
                name="password"
                control={registerControl}
                render={({ field }) => (
                  <Box>
                    <PasswordInput
                      {...field}
                      label="Пароль"
                      placeholder="Введите пароль"
                      leftSection={<IconLock size={16} />}
                      error={registerErrors.password?.message}
                      disabled={isLoading}
                      visibilityToggleIcon={({ reveal }) =>
                        reveal ? <IconEyeOff size={16} /> : <IconEye size={16} />
                      }
                    />
                    {field.value && (
                      <Group justify="space-between" mt="xs">
                        <Text size="xs" c="dimmed">
                          Сложность пароля:
                        </Text>
                        <Text size="xs" c={getPasswordStrength(field.value).color} fw={500}>
                          {getPasswordStrength(field.value).text}
                        </Text>
                      </Group>
                    )}
                  </Box>
                )}
              />

              <Controller
                name="confirmPassword"
                control={registerControl}
                render={({ field }) => (
                  <PasswordInput
                    {...field}
                    label="Подтвердите пароль"
                    placeholder="Повторите пароль"
                    leftSection={<IconLock size={16} />}
                    error={registerErrors.confirmPassword?.message}
                    disabled={isLoading}
                    visibilityToggleIcon={({ reveal }) =>
                      reveal ? <IconEyeOff size={16} /> : <IconEye size={16} />
                    }
                  />
                )}
              />

              <Box>
                <Text size="xs" c="dimmed">
                  Пароль должен содержать:
                </Text>
                <Stack gap={4} mt={4}>
                  <Text size="xs" c="dimmed">
                    • Минимум 6 символов
                  </Text>
                  <Text size="xs" c="dimmed">
                    • Заглавную и строчную буквы
                  </Text>
                  <Text size="xs" c="dimmed">
                    • Хотя бы одну цифру
                  </Text>
                </Stack>
              </Box>

              <Button
                size="lg"
                loading={isLoading}
                disabled={isLoading || isSuccess}
                onClick={handleRegisterSubmit(handleRegister)}
                leftSection={<IconUserPlus size={16} />}
                fullWidth
              >
                {isLoading ? 'Создание аккаунта...' : 'Зарегистрироваться'}
              </Button>
            </Stack>
          )}

          <Divider />
          <Center>
            <Text size="xs" c="dimmed" ta="center">
              Нажимая кнопку "{mode === 'login' ? 'Войти' : 'Зарегистрироваться'}", вы соглашаетесь
              с условиями использования
            </Text>
          </Center>
        </Stack>
      </Modal>
      <ShowOnly when="anonymous">
        <Button
          size="sm"
          leftSection={<IconLogin size={20} />}
          onClick={() => {
            resetSignIn();
            resetSignUp();
            setModalOpened(true);
          }}
        >
          Войти
        </Button>
      </ShowOnly>
      <ShowOnly when="authorized">
        <UserAvatar />
      </ShowOnly>
    </>
  );
};
