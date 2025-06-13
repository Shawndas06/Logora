import { ActionIcon, Badge, Box, Button, Card, Group, Menu, Modal, Stack, Text } from "@mantine/core";
import { IconBuilding, IconCreditCard, IconDots, IconMapPin, IconToggleLeft, IconToggleRight, IconTrash, IconUser } from "@tabler/icons-react";
import { useState } from "react";
import type { Account } from "~/shared/api";
import { useRemoveAccountMutation, useUpdateAccountMutation } from "../../api";
import { notifications } from "@mantine/notifications";

type Props = {
  account: Account;
  onSelect: (account: Account) => void;
};

export const AccountCard = ({ account, onSelect }: Props) => {
const [deleteModalOpened, setDeleteModalOpened] = useState(false);

  const { remove, isLoading } = useRemoveAccountMutation();
  const { update } = useUpdateAccountMutation();

  const handleDelete = () => {
    remove(
      { accountId: account.id },
      {
        onSuccess: () => {
          notifications.show({
            title: 'Успешно',
            message: 'Лицевой счёт успешно удален',
            color: 'green',
          });
          setDeleteModalOpened(false);
        },
        onError: () => {
          notifications.show({
            title: 'Ошибка',
            message: 'Произошла ошибка при удалении лицевого счёта. Попробуйте позже',
            color: 'red',
          });
        },
      }
    );
  };

  const handleUpdate = () => {
    update(
      { accountId: account.id, isActive: !account.isActive },
      {
        onSuccess: () => {
          notifications.show({
            title: 'Успешно',
            message: `Лицевой счёт ${account.isActive ? 'неактивен' : 'активен'}`,
            color: 'green',
          });
        },
        onError: () => {
          notifications.show({
            title: 'Ошибка',
            message: 'Произошла ошибка при обновлении статуса лицевого счёта. Попробуйте позже',
            color: 'red',
          });
        },
      }
    );
  }

  return (
    <>
      <Card
        shadow="sm"
        padding="lg"
        radius="md"
        withBorder
        style={{
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          position: 'relative'
        }}
        onClick={() => onSelect(account)}
      >
        {/* Header with account number and actions */}
        <Group justify="space-between" mb="md">
          <Group gap="xs">
            <IconCreditCard size={18} color={account.isActive ? "#228be6" : "#868e96"} />
              <Text 
              fw={600} 
              size="lg" 
              c={account.isActive ? "blue" : "dimmed"}
            >
              #{account.number}
            </Text>
          </Group>
          <Group gap="xs">
            <Badge 
              color={account.isActive ? "green" : "gray"} 
              variant="light" 
              size="sm"
            >
              {account.isActive ? "Активен" : "Неактивен"}
            </Badge>
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <ActionIcon
                  variant="subtle"
                  color="gray"
                  size="sm"
                  onClick={(e) => e.stopPropagation()}
                >
                  <IconDots size={16} />
                </ActionIcon>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Item
                  leftSection={account.isActive ? 
                    <IconToggleLeft size={14} /> : 
                    <IconToggleRight size={14} />
                  }
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUpdate()
                  }}
                >
                  {account.isActive ? 'Сделать неактивным' : 'Сделать активным'}
                </Menu.Item>
                
                <Menu.Divider />
                
                <Menu.Item
                  color="red"
                  leftSection={<IconTrash size={14} />}
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteModalOpened(true);
                  }}
                >
                  Удалить
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>

        <Box mb="sm">
          <Group gap="xs" mb={4}>
            <IconUser size={16} color="#868e96" />
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Владелец
            </Text>
          </Group>
          <Text size="sm" fw={500} ta="left" pl="26px" >
            {account.ownerFullName}
          </Text>
        </Box>

        {/* Address */}
        <Box mb="sm">
          <Group gap="xs" mb={4}>
            <IconMapPin size={16} color="#868e96" />
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Адрес
            </Text>
          </Group>
          <Text size="sm" fw={500} lineClamp={2} ta="left" pl="26px" >
            {account.address}
          </Text>
        </Box>

        {/* Company */}
        <Box mb="md">
          <Group gap="xs" mb={4}>
            <IconBuilding size={16} color="#868e96" />
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Управляющая Компания
            </Text>
          </Group>
          <Text size="sm" fw={500} ta="left" pl="26px" >
            {account.companyName}
          </Text>
        </Box>

        {/* Property info */}
        <Group justify="space-between" pt="sm" style={{ borderTop: '1px solid #e9ecef' }}>
          <Box ta="center">
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Площадь
            </Text>
            <Text size="sm" fw={600}>
              {account.propertySquare} м²
            </Text>
          </Box>
          <Box ta="center">
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Жильцов
            </Text>
            <Text size="sm" fw={600}>
              {account.residentsCount} чел.
            </Text>
          </Box>
        </Group>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal
        opened={deleteModalOpened}
        onClose={() => setDeleteModalOpened(false)}
        title="Подтверждение удаления"
        centered
        size="sm"
      >
        <Stack gap="md">
          <Text>
            Вы уверены, что хотите удалить лицевой счёт{' '}
            <Text span fw={600} c="blue">
              #{account.number}
            </Text>
            ?
          </Text>
          <Text size="sm" c="dimmed">
            Это действие нельзя будет отменить.
          </Text>
          <Group justify="flex-end">
            <Button 
              variant="subtle" 
              onClick={() => setDeleteModalOpened(false)}
            >
              Отмена
            </Button>
            <Button 
              color="red" 
              onClick={handleDelete}
              loading={isLoading}
            >
              Удалить
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
};

