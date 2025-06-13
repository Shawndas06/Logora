import {
  Alert,
  Box,
  Card,
  Center,
  Container,
  Group,
  Loader,
  Stack,
  Table,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import { IconAlertCircle, IconCreditCard, IconReceipt } from '@tabler/icons-react';
import { usePayments } from '~/entities/payments';

import { useParams } from 'react-router';

export const PaymentHistory = () => {
  const { accountId } = useParams();
  const { data: payments, isLoading, error, refetch } = usePayments(accountId);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <Container size="md" py="xl">
      <Stack gap="xl">
        <Box ta="center">
          <Group justify="center" mb="sm">
            <ThemeIcon size="xl" variant="light" color="blue">
              <IconCreditCard size={28} />
            </ThemeIcon>
          </Group>
          <Title order={2} mb="xs">
            История платежей
          </Title>
          <Text c="dimmed" size="sm">
            Все ваши совершенные платежи
          </Text>
        </Box>

        {isLoading && (
          <Card withBorder padding="xl">
            <Center>
              <Stack align="center" gap="md">
                <Loader size="lg" />
                <Text c="dimmed">Загрузка истории платежей...</Text>
              </Stack>
            </Center>
          </Card>
        )}

        {error && (
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Ошибка загрузки"
            color="red"
            variant="light"
          >
            <Stack gap="sm">
              <Group>
                <Text size="xs" c="dimmed">
                  Попробуйте обновить страницу или повторить запрос
                </Text>
                <Text
                  size="xs"
                  c="blue"
                  style={{ cursor: 'pointer', textDecoration: 'underline' }}
                  onClick={refetch}
                >
                  Повторить
                </Text>
              </Group>
            </Stack>
          </Alert>
        )}

        {!isLoading && !error && payments?.length === 0 && (
          <Card withBorder padding="xl">
            <Stack align="center" gap="md">
              <ThemeIcon size={60} variant="light" color="gray" radius="xl">
                <IconReceipt size={30} />
              </ThemeIcon>
              <Title order={3} c="dimmed" ta="center">
                Нет платежей
              </Title>
              <Text c="dimmed" ta="center" size="sm">
                У вас пока нет совершенных платежей. Платежи будут отображаться здесь после их
                выполнения.
              </Text>
            </Stack>
          </Card>
        )}

        {/* Payments Table */}
        {!isLoading && !error && payments && payments.length > 0 && (
          <Card withBorder padding={0}>
            <Table highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>
                    <Text fw={600}>Дата платежа</Text>
                  </Table.Th>
                  <Table.Th ta="right">
                    <Text fw={600}>Сумма</Text>
                  </Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {payments.map((payment) => (
                  <Table.Tr key={payment.id}>
                    <Table.Td>
                      <Text size="sm" c="dark">
                        {formatDate(payment.createdAt)}
                      </Text>
                    </Table.Td>
                    <Table.Td ta="right">
                      <Text size="lg" fw={700} c="green">
                        {formatCurrency(payment.amount)}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>

            {/* Summary */}
            <Box p="md" bg="gray.0" style={{ borderTop: '1px solid var(--mantine-color-gray-3)' }}>
              <Group justify="space-between">
                <Text size="sm" c="dimmed">
                  Всего платежей:{' '}
                  <Text span fw={500}>
                    {payments.length}
                  </Text>
                </Text>
                <Text size="sm" fw={600}>
                  Общая сумма:{' '}
                  <Text span c="green" fw={700}>
                    {formatCurrency(payments.reduce((sum, p) => sum + p.amount, 0))}
                  </Text>
                </Text>
              </Group>
            </Box>
          </Card>
        )}
      </Stack>
    </Container>
  );
};
