import { ActionIcon, Avatar, Box, Group, Menu, Text } from '@mantine/core';
import {
  IconLogout,
} from '@tabler/icons-react';

import { useLogoutMutation } from '../../api';
import { useAuthContext } from '~/shared/session';

export const UserAvatar = () => {
  const { user } = useAuthContext();
  const { logout, isLoading } = useLogoutMutation();

  const handleLogout = () => {
    logout();
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((word) => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (name: string) => {
    const colors = ['blue', 'green', 'red', 'orange', 'purple', 'teal', 'pink', 'indigo'];
    const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  if (!user) {
    return null;
  }

  return (
    <Menu shadow="md" width={280} position="bottom-end" withArrow>
      <Menu.Target>
        <ActionIcon variant="subtle" size="lg" style={{ borderRadius: '50%' }}>
          <Avatar
            size="md"
            color={getAvatarColor(user.username)}
            style={{ cursor: 'pointer' }}
          >
            {getInitials(user.username)}
          </Avatar>
        </ActionIcon>
      </Menu.Target>

      <Menu.Dropdown>
        <Box p="md" pb="xs">
          <Group>
            <Avatar size="lg" color={getAvatarColor(user.username)}>
              {getInitials(user.username)}
            </Avatar>
            <Box style={{ flex: 1 }}>
              <Text fw={600} size="sm">
                {user.username}
              </Text>
              <Text size="xs" c="dimmed">
                {user.username}
              </Text>
            </Box>
          </Group>
        </Box>
        <Menu.Item
          color="red"
          leftSection={<IconLogout size={16} />}
          onClick={handleLogout}
          disabled={isLoading}
        >
          {isLoading ? 'Выход...' : 'Выйти'}
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  );
};
