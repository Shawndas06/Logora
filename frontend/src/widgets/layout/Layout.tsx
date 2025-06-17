import { AppShell, Burger, Group, NavLink as Link, Stack } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { AuthModal } from '~/features/auth';
import { ShowOnly } from '~/shared/ui/showOnly';

import { NavLink, useLocation } from 'react-router';

import styles from './Layout.module.scss';

type Props = {
  children?: React.ReactNode;
};

const MENU_ITEMS = [
  {
    label: 'Главная',
    link: '/',
  },
  {
    label: 'Лицевые счета',
    link: '/accounts',
    protected: true,
  },
  {
    label: 'Заявки',
    link: '/orders',
    protected: true,
  },
];

export const Layout = ({ children }: Props) => {
  const [opened, { toggle }] = useDisclosure();
  const { pathname } = useLocation();

  const isHomePage = pathname === '/';

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm', collapsed: { desktop: true, mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Group justify="space-between" style={{ flex: 1 }}>
            <Group ml="xl" gap={0} visibleFrom="sm">
              {MENU_ITEMS.map((item) => {
                return (
                  <ShowOnly key={item.label} when={item.protected ? 'authorized' : undefined}>
                    <NavLink to={item.link}>
                      {({ isActive }) => (
                        <Link component="span" label={item.label} active={isActive} />
                      )}
                    </NavLink>
                  </ShowOnly>
                );
              })}
            </Group>
            <div className={styles.title}>Smart</div>
            <AuthModal />
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar py="md" px={4}>
        <Stack justify="space-between" gap={16}>
          {MENU_ITEMS.map((item) => (
            <ShowOnly key={item.label} when={item.protected ? 'authorized' : undefined}>
              <NavLink to={item.link}>
                {({ isActive }) => <Link component="span" label={item.label} active={isActive} />}
              </NavLink>
            </ShowOnly>
          ))}
          {/* <AuthModal /> */}
        </Stack>
      </AppShell.Navbar>

      <AppShell.Main p={isHomePage ? '0' : undefined}>{children}</AppShell.Main>
    </AppShell>
  );
};
