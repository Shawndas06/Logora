import { Button, Card, Container, Group, SimpleGrid, Stack, Text, Title } from '@mantine/core';
import { IconCreditCard, IconPlus } from '@tabler/icons-react';
import { AccountCard, useAccounts } from '~/entities/accounts';
import { CreateAccountForm } from '~/features/createAccount';
import type { Account } from '~/shared/api';

import { useState } from 'react';
import { useNavigate } from 'react-router';

export const Accounts = () => {
  const { data, isSuccess } = useAccounts();
  const navigate = useNavigate();

  const [modalOpened, setModalOpened] = useState(false);

  const handleAccountSelect = (account: Account) => {
    navigate(`/accounts/${account.id}`);
  };

  if (isSuccess && data.length === 0) {
    return (
      <Container size="md" py="xl">
        <Card shadow="sm" padding="xl" radius="md" withBorder>
          <Stack align="center" gap="md">
            <IconCreditCard size={48} color="#ced4da" />
            <Title order={3} c="dimmed">
              Нет лицевых счетов
            </Title>
            <Text c="dimmed" ta="center">
              У вас пока нет добавленных лицевых счетов. Добавьте первый счёт, чтобы начать работу.
            </Text>
            <Button leftSection={<IconPlus size={16} />} onClick={() => setModalOpened(true)}>
              Добавить счёт
            </Button>
          </Stack>
        </Card>

        <CreateAccountForm
          opened={modalOpened}
          onClose={() => setModalOpened(false)}
        />
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Stack gap="xl">
        <Group justify="space-between">
          <Title order={1}>Лицевые счета</Title>
          <Button leftSection={<IconPlus size={16} />} onClick={() => setModalOpened(true)}>
            Добавить счёт
          </Button>
        </Group>

        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
          {data.map((account) => (
            <AccountCard
              key={account.id}
              account={account}
              onSelect={handleAccountSelect}
            />
          ))}
        </SimpleGrid>
      </Stack>

      <CreateAccountForm
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
      />
    </Container>
  );
};
