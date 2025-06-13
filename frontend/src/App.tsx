import { createTheme, MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import { Notifications } from '@mantine/notifications';
import '@mantine/notifications/styles.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Account } from '~/pages/account';
import { Accounts } from '~/pages/accounts';
import { Home } from '~/pages/home';
import { PaymentHistory } from '~/pages/paymentHistory';

import { BrowserRouter, Route, Routes } from 'react-router';

import './App.css';
import { ProtectedRoute } from './shared/routing';
import { AuthProvider } from './shared/session';
import { Layout } from './widgets/layout';

const theme = createTheme({});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App = () => {
  return (
    <MantineProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <Notifications />
            <Layout>
              <Routes>
                <Route path="/" index element={<Home />} />
                <Route path="accounts">
                  <Route
                    index
                    element={
                      <ProtectedRoute>
                        <Accounts />
                      </ProtectedRoute>
                    }
                  />
                  <Route path=":accountId/payments" element={<PaymentHistory />} />
                  <Route
                    path=":accountId"
                    element={
                      <ProtectedRoute>
                        <Account />
                      </ProtectedRoute>
                    }
                  />
                </Route>
              </Routes>
            </Layout>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </MantineProvider>
  );
};
