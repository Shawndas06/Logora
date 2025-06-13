import type { ReactNode } from 'react';
import { useAuthContext } from '~/shared/session';

type Props = {
  when?: 'authorized' | 'anonymous';
  children: ReactNode;
};

export function ShowOnly({ when, children }: Props) {
  const { isAuthenticated } = useAuthContext();

  if (when === 'authorized') {
    if (!isAuthenticated) {
      return null;
    }
  }

  if (isAuthenticated && when === 'anonymous') {
    return null;
  }

  return <>{children}</>;
}
