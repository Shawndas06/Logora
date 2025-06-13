import { zodResolver } from '@hookform/resolvers/zod';
import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Divider,
  Group,
  Modal,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Title,
  Tooltip,
} from '@mantine/core';
import {
  IconBrandApple,
  IconBrandGoogle,
  IconBrandMastercard,
  IconBrandPaypal,
  IconBrandVisa,
  IconCheck,
  IconCreditCard,
  IconInfoCircle,
  IconLock,
  IconShield,
  IconX,
} from '@tabler/icons-react';
import { z } from 'zod';

import React, { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';

import { usePayMutation } from '../../api';

// Validation schemas
const creditCardSchema = z.object({
  cardNumber: z
    .string()
    .min(1, 'Номер карты обязателен')
    .regex(/^\d{4}\s\d{4}\s\d{4}\s\d{4}$/, 'Неверный формат номера карты')
    .refine((val) => {
      const digits = val.replace(/\s/g, '');
      let sum = 0;
      let isEven = false;

      for (let i = digits.length - 1; i >= 0; i--) {
        let digit = parseInt(digits[i]);
        if (isEven) {
          digit *= 2;
          if (digit > 9) digit -= 9;
        }
        sum += digit;
        isEven = !isEven;
      }

      return sum % 10 === 0;
    }, 'Неверный номер карты'),

  expiryDate: z
    .string()
    .min(1, 'Срок действия обязателен')
    .regex(/^(0[1-9]|1[0-2])\/\d{2}$/, 'Неверный формат (MM/YY)')
    .refine((val) => {
      const [month, year] = val.split('/');
      const currentDate = new Date();
      const currentYear = currentDate.getFullYear() % 100;
      const currentMonth = currentDate.getMonth() + 1;

      const expYear = parseInt(year);
      const expMonth = parseInt(month);

      if (expYear < currentYear) return false;
      if (expYear === currentYear && expMonth < currentMonth) return false;

      return true;
    }, 'Карта просрочена'),

  cvv: z
    .string()
    .min(1, 'CVV обязателен')
    .regex(/^\d{3,4}$/, 'CVV должен содержать 3-4 цифры'),

  cardholderName: z
    .string()
    .min(1, 'Имя владельца обязательно')
    .min(3, 'Имя должно содержать минимум 3 символа')
    .regex(/^[a-zA-Z\s]+$/, 'Имя должно содержать только латинские буквы'),
});

type CreditCardFormData = z.infer<typeof creditCardSchema>;

interface PaymentMethod {
  id: string;
  name: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  icon: React.ComponentType<any>;
  color: string;
  description: string;
  fees?: string;
  processingTime?: string;
}

type Props = {
  accountId: number;
  billingIds: number[];
  amount: number;
};

const paymentMethods: PaymentMethod[] = [
  {
    id: 'google-pay',
    name: 'Google Pay',
    icon: IconBrandGoogle,
    color: 'blue',
    description: 'Быстрая и безопасная оплата',
    processingTime: 'Мгновенно',
  },
  {
    id: 'apple-pay',
    name: 'Apple Pay',
    icon: IconBrandApple,
    color: 'dark',
    description: 'Оплата одним касанием',
    processingTime: 'Мгновенно',
  },
  {
    id: 'paypal',
    name: 'PayPal',
    icon: IconBrandPaypal,
    color: 'blue',
    description: 'Международная платежная система',
    fees: 'Комиссия 2.9%',
    processingTime: '1-2 минуты',
  },
  {
    id: 'credit-card',
    name: 'Банковская карта',
    icon: IconCreditCard,
    color: 'green',
    description: 'Visa, Mastercard, МИР',
    processingTime: '1-3 минуты',
  },
];

export const Pay = ({ amount, billingIds, accountId }: Props) => {
  const [modalOpened, setModalOpened] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const { pay, reset: resetPayment, isLoading, error, isSuccess } = usePayMutation();

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<CreditCardFormData>({
    resolver: zodResolver(creditCardSchema),
    reValidateMode: 'onChange',
    defaultValues: {
      cardNumber: '',
      expiryDate: '',
      cvv: '',
      cardholderName: '',
    },
  });

  const cardNumber = watch('cardNumber');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
    }).format(amount);
  };

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];

    for (let i = 0; i < match.length; i += 4) {
      parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const formatExpiryDate = (value: string) => {
    const v = value.replace(/\D/g, '');
    if (v.length >= 2) {
      return `${v.slice(0, 2)}/${v.slice(2, 4)}`;
    }
    return v;
  };

  const getCardType = (number: string) => {
    const cleanNumber = number.replace(/\s/g, '');
    if (cleanNumber.startsWith('4')) return 'visa';
    if (cleanNumber.startsWith('5') || cleanNumber.startsWith('2')) return 'mastercard';
    if (cleanNumber.startsWith('2')) return 'mir';
    return null;
  };

  const handleCardNumberChange = (value: string) => {
    const formatted = formatCardNumber(value);
    setValue('cardNumber', formatted);
  };

  const handleExpiryDateChange = (value: string) => {
    const formatted = formatExpiryDate(value);
    setValue('expiryDate', formatted);
  };

  const handlePayment = async (data?: CreditCardFormData) => {
    if (!selectedMethod) return;

    setErrorMessage('');

    pay({
        accountId: Number(accountId),
        billingIds,
        amount,
        creditCard: data,
    }, {
      onSuccess: () => {
        setTimeout(() => {
          handleClose();
        }, 2000);
      },
      onError: () => {
        setErrorMessage('Произошла ошибка при обработке платежа');
      }
    });
  };

  const handleMethodSelect = (methodId: string) => {
    setSelectedMethod(methodId);
    setErrorMessage('');
  };

  const handleClose = () => {
    setSelectedMethod(null);
    setErrorMessage('');
    reset();
    resetPayment();
    setModalOpened(false);
  };

  const renderPaymentForm = () => {
    if (!selectedMethod) return null;

    const method = paymentMethods.find((m) => m.id === selectedMethod);
    if (!method) return null;

    if (selectedMethod === 'credit-card') {
      return (
        <Stack gap="lg">
          <Alert icon={<IconShield size={16} />} title="Безопасность" color="blue" variant="light">
            Все данные передаются по защищенному соединению SSL
          </Alert>

          {/* Card Preview */}
          <Paper
            withBorder
            p="lg"
            radius="md"
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
          >
            <Stack gap="md">
              <Group justify="space-between">
                <Group>
                  <IconCreditCard size={24} color="white" />
                  <Text size="sm" c="white" fw={500}>
                    {getCardType(cardNumber) === 'visa'
                      ? 'VISA'
                      : getCardType(cardNumber) === 'mastercard'
                        ? 'MASTERCARD'
                        : 'КАРТА'}
                  </Text>
                </Group>
                {getCardType(cardNumber) && (
                  <ThemeIcon size="lg" variant="white" color="gray">
                    {getCardType(cardNumber) === 'visa' ? (
                      <IconBrandVisa />
                    ) : (
                      <IconBrandMastercard />
                    )}
                  </ThemeIcon>
                )}
              </Group>

              <Text size="lg" ff="monospace" c="white" fw={600}>
                {cardNumber || '•••• •••• •••• ••••'}
              </Text>

              <Group justify="space-between">
                <Text size="xs" c="white" opacity={0.8}>
                  {watch('cardholderName') || 'CARDHOLDER NAME'}
                </Text>
                <Text size="xs" c="white" opacity={0.8}>
                  {watch('expiryDate') || 'MM/YY'}
                </Text>
              </Group>
            </Stack>
          </Paper>

          {/* Form Fields */}
          <SimpleGrid cols={1} spacing="md">
            <Controller
              name="cardNumber"
              control={control}
              render={({ field }) => (
                <TextInput
                  {...field}
                  label="Номер карты"
                  placeholder="1234 5678 9012 3456"
                  leftSection={<IconCreditCard size={16} />}
                  error={errors.cardNumber?.message}
                  maxLength={19}
                  onChange={(e) => handleCardNumberChange(e.target.value)}
                />
              )}
            />

            <Controller
              name="cardholderName"
              control={control}
              render={({ field }) => (
                <TextInput
                  {...field}
                  label="Имя владельца (как на карте)"
                  placeholder="JOHN SMITH"
                  error={errors.cardholderName?.message}
                  style={{ textTransform: 'uppercase' }}
                />
              )}
            />

            <Group grow>
              <Controller
                name="expiryDate"
                control={control}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    label="Срок действия"
                    placeholder="MM/YY"
                    error={errors.expiryDate?.message}
                    maxLength={5}
                    onChange={(e) => handleExpiryDateChange(e.target.value)}
                  />
                )}
              />

              <Controller
                name="cvv"
                control={control}
                render={({ field }) => (
                  <TextInput
                    {...field}
                    label="CVV"
                    placeholder="123"
                    error={errors.cvv?.message}
                    maxLength={4}
                    rightSection={
                      <Tooltip label="3-4 цифры на обратной стороне карты">
                        <IconInfoCircle
                          size={16}
                          style={{ color: 'var(--mantine-color-dimmed)' }}
                        />
                      </Tooltip>
                    }
                  />
                )}
              />
            </Group>
          </SimpleGrid>

          {errorMessage && (
            <Alert color="red" icon={<IconX size={16} />}>
              {errorMessage}
            </Alert>
          )}

          {isSuccess && (
            <Alert color="green" icon={<IconCheck size={16} />}>
              Платеж успешно обработан!
            </Alert>
          )}

          <Button
            size="lg"
            loading={isLoading}
            disabled={isLoading || isSuccess}
            leftSection={<IconLock size={16} />}
            onClick={handleSubmit(handlePayment)}
            fullWidth
          >
            {isLoading ? 'Обработка платежа...' : `Оплатить ${formatCurrency(amount)}`}
          </Button>
        </Stack>
      );
    }

    return (
      <Stack gap="md">
        <Alert
          icon={<method.icon size={16} />}
          title={method.name}
          color={method.color}
          variant="light"
        >
          {method.description}
          {method.processingTime && (
            <Text size="sm" mt="xs">
              Время обработки: {method.processingTime}
            </Text>
          )}
        </Alert>

        {error && (
          <Alert color="red" icon={<IconX size={16} />}>
            {errorMessage}
          </Alert>
        )}

        {isSuccess && (
          <Alert color="green" icon={<IconCheck size={16} />}>
            Платеж успешно обработан!
          </Alert>
        )}

        <Button
          size="lg"
          color={method.color}
          loading={isLoading}
          disabled={isLoading || isSuccess}
          leftSection={<method.icon size={16} />}
          onClick={() => handlePayment()}
          fullWidth
        >
          {isLoading ? 'Обработка...' : `Оплатить через ${method.name}`}
        </Button>
      </Stack>
    );
  };

  if (amount <= 0) {
    return null;
  }

  return (
    <>
      <Modal
        opened={modalOpened}
        onClose={handleClose}
        title={
          <Group>
            <IconLock size={20} />
            <Title order={3}>Оплата счёта</Title>
          </Group>
        }
        size="lg"
        centered
      >
        <Stack gap="xl">
          <Paper withBorder p="md" radius="md" bg="gray.0">
            <Group justify="space-between">
              <Box>
                <Text size="sm" c="dimmed">
                  К оплате
                </Text>
                <Text size="xl" fw={700} c="blue">
                  {formatCurrency(amount)}
                </Text>
              </Box>
            </Group>
          </Paper>

          {!selectedMethod ? (
            <Stack gap="md">
              <Title order={4}>Выберите способ оплаты</Title>

              <SimpleGrid cols={1} spacing="sm">
                {paymentMethods.map((method) => (
                  <Card
                    key={method.id}
                    withBorder
                    padding="md"
                    radius="md"
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleMethodSelect(method.id)}
                  >
                    <Group justify="space-between">
                      <Group>
                        <ThemeIcon size="lg" variant="light" color={method.color}>
                          <method.icon size={20} />
                        </ThemeIcon>
                        <Box>
                          <Text fw={600}>{method.name}</Text>
                          <Text size="sm" c="dimmed">
                            {method.description}
                          </Text>
                        </Box>
                      </Group>
                      <Group gap="xs">
                        {method.fees && (
                          <Badge color="orange" variant="light" size="sm">
                            {method.fees}
                          </Badge>
                        )}
                        {method.processingTime && (
                          <Badge color="blue" variant="light" size="sm">
                            {method.processingTime}
                          </Badge>
                        )}
                      </Group>
                    </Group>
                  </Card>
                ))}
              </SimpleGrid>
            </Stack>
          ) : (
            <Stack gap="md">
              <Group>
                <ActionIcon
                  variant="subtle"
                  onClick={() => setSelectedMethod(null)}
                  disabled={isLoading}
                >
                  <IconX size={16} />
                </ActionIcon>
                <Title order={4}>{paymentMethods.find((m) => m.id === selectedMethod)?.name}</Title>
              </Group>

              <Divider />

              {renderPaymentForm()}
            </Stack>
          )}

          {/* Security Notice */}
          <Group justify="center" mt="md">
            <Group gap="xs">
              <IconShield size={16} color="var(--mantine-color-dimmed)" />
              <Text size="xs" c="dimmed" ta="center">
                Защищено 256-битным SSL шифрованием
              </Text>
            </Group>
          </Group>
        </Stack>
      </Modal>
      <Button
        size="md"
        variant='outline'
        leftSection={<IconCreditCard size={20} />}
        onClick={() => setModalOpened(true)}
      >
        Оплатить
      </Button>
    </>
  );
};
