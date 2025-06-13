import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Container,
  Divider,
  Group,
  Loader,
  Paper,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import {
  IconAlertCircle,
  IconArrowLeft,
  IconBolt,
  IconCalendar,
  IconDroplet,
  IconThermometer,
  IconTrash,
  IconWaterpolo,
} from '@tabler/icons-react';
import { useAccount } from '~/entities/accounts';
import { useBillings } from '~/entities/billing';
import { ExportReport } from '~/features/exportReport';
import { Pay } from '~/features/pay';
import type { BillingService } from '~/shared/api';

import { useState } from 'react';
import { NavLink, useNavigate, useParams } from 'react-router';

const periodOptions = [
  { value: '6', label: '6 месяцев' },
  { value: '9', label: '9 месяцев' },
  { value: '12', label: '1 год' },
  { value: '24', label: '2 года' },
];

const utilityConfig = {
  coldWater: { name: 'Холодное водоснабжение', icon: IconDroplet, color: 'blue' },
  hotWater: { name: 'Горячее водоснабжение', icon: IconDroplet, color: 'red' },
  electricity: { name: 'Электроэнергия', icon: IconBolt, color: 'yellow' },
  heating: { name: 'Отопление', icon: IconThermometer, color: 'red' },
  supportion: { name: 'Водоотведение', icon: IconWaterpolo, color: 'orange' },
  maintenance: { name: 'Содержание жилья', icon: IconTrash, color: 'gray' },
  overhaul: { name: 'Капитальный ремонт', icon: IconCalendar, color: 'teal' },
};

export const Account = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('6');
  const { accountId } = useParams();
  const account = useAccount(accountId);
  const navigate = useNavigate();

  const {
    data: billingData,
    isLoading,
    isSuccess,
    error,
    refetch,
  } = useBillings(accountId, Number(selectedPeriod));

  const formatCurrency = (amount: number) => {
    if (amount === 0) return '';
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
    });
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'paid':
        return (
          <Badge color="green" variant="light">
            Оплачено
          </Badge>
        );
      case 'unpaid':
      default:
        return (
          <Badge color="red" variant="light">
            К доплате
          </Badge>
        );
    }
  };

  const groupServicesByMonth = (services: BillingService[]) => {
    const grouped = services.reduce(
      (acc, service) => {
        const monthKey = service.createdAt.substring(0, 7);
        if (!acc[monthKey]) {
          acc[monthKey] = [];
        }
        acc[monthKey].push(service);
        return acc;
      },
      {} as Record<string, BillingService[]>
    );

    return Object.entries(grouped)
      .sort(([a], [b]) => b.localeCompare(a))
      .map(([monthKey, services]) => ({
        month: monthKey,
        services,
        billingIds: services.map((s) => s.id),
        total: services
          .filter(({ status }) => status === 'waiting_for_payment')
          .reduce((sum, s) => sum + s.amount, 0),
      }));
  };

  if (isLoading) {
    return (
      <Stack align="center" gap="md">
        <Loader size="lg" />
        <Text>Загрузка данных о начислениях...</Text>
      </Stack>
    );
  }

  if (error) {
    return (
      <Container size="xl" py="xl">
        <Stack>
          <ActionIcon variant="subtle" size="lg" onClick={() => navigate(-1)}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Ошибка загрузки"
            color="red"
            variant="light"
          >
            Не удалось загрузить данные о лицевых счетах
            <Text
              size="xs"
              c="blue"
              style={{ cursor: 'pointer', textDecoration: 'underline' }}
              onClick={refetch}
            >
              Повторить
            </Text>
          </Alert>
        </Stack>
      </Container>
    );
  }

  if (error || !account) {
    return (
      <Container size="xl" py="xl">
        <Stack>
          <ActionIcon variant="subtle" size="lg" onClick={() => navigate(-1)}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Ошибка загрузки"
            color="red"
            variant="light"
          >
            Не удалось загрузить данные о начислениях.
            <Text
              size="xs"
              c="blue"
              style={{ cursor: 'pointer', textDecoration: 'underline' }}
              onClick={refetch}
            >
              Повторить
            </Text>
          </Alert>
        </Stack>
      </Container>
    );
  }

  if (!billingData) {
    return (
      <Stack align="center" gap="md">
        <Text>Нет активных</Text>
      </Stack>
    );
  }

  const { services, total } = billingData;
  const monthlyData = groupServicesByMonth(services);

  const paidServices = services.filter((s) => s.status === 'paid');
  const unpaidServices = services.filter((s) => s.status !== 'paid');
  const totalPaid = paidServices.reduce((sum, s) => sum + s.amount, 0);
  const totalUnpaid = unpaidServices.reduce((sum, s) => sum + s.amount, 0);
  const unpaidBillingIds = unpaidServices.map((s) => s.id);

  return (
    <Container size="xl" py="xl">
      <Stack gap="xl">
        <Group justify="space-between">
          <Group>
            <ActionIcon variant="subtle" size="lg" onClick={() => navigate(-1)}>
              <IconArrowLeft size={20} />
            </ActionIcon>
            <Box>
              <Title order={2}>Лицевой счёт #{account.number}</Title>
              <Text c="dimmed" size="sm">
                {account.address}
              </Text>
            </Box>
          </Group>
          <Group>
            <NavLink to={`/accounts/${accountId}/payments`}>
              {() => <Button>История платежей</Button>}
            </NavLink>
            <Select
              data={periodOptions}
              value={selectedPeriod}
              onChange={(value) => setSelectedPeriod(value || '6')}
              leftSection={<IconCalendar size={16} />}
              w={150}
            />
            {accountId && <ExportReport accountId={parseInt(accountId)} />}
          </Group>
        </Group>

        {isSuccess && billingData?.services.length === 0 ?
          <Alert
            w="100%"
            icon={<IconAlertCircle size={16} />}
            title="Пусто :("
            color="indigo"
            variant="light"
            ta="left"
          >
            Нет начислений за выбранный период.
          </Alert>
        :

          <>
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="lg">
          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Text size="sm" c="dimmed" fw={500}>
                К доплате
              </Text>
              <Text size="xl" fw={700} c="red">
                {formatCurrency(totalUnpaid)}
              </Text>
              <Badge color="red" variant="light" size="sm">
                {unpaidServices.length} начислений
              </Badge>
            </Stack>
          </Card>

          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Text size="sm" c="dimmed" fw={500}>
                Оплачено
              </Text>
              <Text size="xl" fw={700} c="green">
                {formatCurrency(totalPaid)}
              </Text>
              <Badge color="green" variant="light" size="sm">
                {paidServices.length} начислений
              </Badge>
            </Stack>
          </Card>

          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Text size="sm" c="dimmed" fw={500}>
                Всего за период
              </Text>
              <Text size="xl" fw={700}>
                {formatCurrency(total.amount)}
              </Text>
              <Badge variant="light" size="sm">
                {services.length} начислений
              </Badge>
            </Stack>
          </Card>

          <Card withBorder padding="lg">
            <Stack gap="xs">
              <Text size="sm" c="dimmed" fw={500}>
                Средний платеж
              </Text>
              <Text size="xl" fw={700}>
                {formatCurrency(total.amount / parseInt(selectedPeriod))}
              </Text>
              <Badge color="blue" variant="light" size="sm">
                в месяц
              </Badge>
            </Stack>
          </Card>
        </SimpleGrid>

        {!!totalUnpaid && <Card withBorder padding="lg">
          <Stack gap="md">
            <Group justify="space-between">
              <Group>
                <Title order={4}>Всего к оплате</Title>
              </Group>
              <Group>
                <Text size="lg" fw={700}>
                  {formatCurrency(totalUnpaid)}
                </Text>
                <Group gap="xs">
                  <Pay
                    accountId={Number(accountId)}
                    billingIds={unpaidBillingIds}
                    amount={totalUnpaid}
                  />
                </Group>
              </Group>
            </Group>
          </Stack>
        </Card>}

        <Stack gap="lg" mt="xl">
          <Title order={1}>Начисления по месяцам</Title>

          {monthlyData.map((monthData) => (
            <Card key={monthData.month} withBorder padding="lg">
              <Stack gap="md">
                <Group justify="space-between">
                  <Group>
                    <Title order={4}>{formatDate(monthData.month + '-01')}</Title>
                    {getStatusBadge(monthData.services[0]?.status)}
                  </Group>
                  <Group>
                    <Text size="lg" fw={700}>
                      {formatCurrency(monthData.total)}
                    </Text>
                    <Group gap="xs">
                      <Pay
                        accountId={Number(accountId)}
                        billingIds={monthData.billingIds}
                        amount={monthData.total}
                      />
                    </Group>
                  </Group>
                </Group>

                <Divider />

                <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
                  {monthData.services.map((service, index) => {
                    const config = utilityConfig[service.type];

                    if (service.amount === 0) {
                      return null;
                    }

                    return (
                      <Paper key={`${service.type}-${index}`} withBorder p="md" radius="md">
                        <Group justify="space-between" mb="xs">
                          <Group gap="xs">
                            <ThemeIcon size="sm" variant="light" color={config.color}>
                              <config.icon size={14} />
                            </ThemeIcon>
                            <Text size="xs" fw={600} tt="uppercase" c="dimmed">
                              {config.name}
                            </Text>
                          </Group>
                          {getStatusBadge(service.status)}
                        </Group>

                        <Stack gap={4}>
                          <Group justify="space-between">
                            <Text size="xs" c="dimmed">
                              Дата начисления:
                            </Text>
                            <Text size="xs" fw={500}>
                              {new Date(service.createdAt).toLocaleDateString('ru-RU')}
                            </Text>
                          </Group>
                          <Divider size="xs" />
                          <Group justify="space-between">
                            <Text size="sm" fw={600}>
                              Сумма:
                            </Text>
                            <Text size="sm" fw={700} c={service.amount > 0 ? 'dark' : 'dimmed'}>
                              {formatCurrency(service.amount)}
                            </Text>
                          </Group>
                        </Stack>
                      </Paper>
                    );
                  })}
                </SimpleGrid>
              </Stack>
            </Card>
          ))}
        </Stack>

        <Card withBorder padding="lg">
          <Stack gap="md">
            <Title order={3}>Сводка по видам услуг</Title>

            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Вид услуги</Table.Th>
                  <Table.Th ta="right">Количество начислений</Table.Th>
                  <Table.Th ta="right">Всего за период</Table.Th>
                  <Table.Th ta="right">Средняя сумма</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {total.services.map((totalService) => {
                  const config = utilityConfig[totalService.type];
                  const serviceCount = services.filter((s) => s.type === totalService.type).length;
                  const avgAmount = serviceCount > 0 ? totalService.amount / serviceCount : 0;

                  return (
                    <Table.Tr key={totalService.type}>
                      <Table.Td>
                        <Group gap="xs">
                          <ThemeIcon size="sm" variant="light" color={config.color}>
                            <config.icon size={14} />
                          </ThemeIcon>
                          <Text size="sm">{config.name}</Text>
                        </Group>
                      </Table.Td>
                      <Table.Td ta="right">
                        <Text size="sm">{serviceCount}</Text>
                      </Table.Td>
                      <Table.Td ta="right">
                        <Text size="sm" fw={600}>
                          {formatCurrency(totalService.amount)}
                        </Text>
                      </Table.Td>
                      <Table.Td ta="right">
                        <Text size="sm">{formatCurrency(avgAmount)}</Text>
                      </Table.Td>
                    </Table.Tr>
                  );
                })}
              </Table.Tbody>
            </Table>
          </Stack>
        </Card>
        </>}
      </Stack>
    </Container>
  );
};
