/* eslint-disable @typescript-eslint/no-unused-vars */
import { BACKEND_URL } from '../config';

type Success<D = undefined> = {
  success: true;
} & { data: D };

export type User = {
  id: number;
  username: string;
  email: string
  is_admin: boolean;
  name: string;
  sex: 1 | 0;
  description: string;
};

export type Account = {
  id: number;
  number: string;
  isActive: boolean;
  address: string;
  ownerFullName: string;
  propertySquare: number;
  residentsCount: number;
  companyName: string;
};

export type CreateAccount  = Omit<Account, 'id' | 'isActive'>;

type UtilityType =
  | 'coldWater'
  | 'hotWater'
  | 'electricity'
  | 'heating'
  | 'supportion'
  | 'maintenance'
  | 'overhaul';

export type BillingService = {
  id: number;
  type: UtilityType;
  createdAt: string;
  amount: number;
  status: 'paid' | 'waiting_for_payment';
};

export type BillingServiceTotal = {
  type: UtilityType;
  amount: number;
}

export type Billing = {
  services: BillingService[];
  total: {
    services: BillingServiceTotal[];
    amount: number;
  };
};

export type Payment = {
  id: number;
  account_id: number;
  billing_ids: number[];
  amount: number;
  created_at: string;
  status: 'processing' | 'completed' | 'error';
};

// @ts-expect-error debug
const payments = [{
            id: 'pay-001',
            amount: 3247.50,
            date: '2024-12-01T10:30:00.000Z'
          },
          {
            id: 'pay-002',
            amount: 2891.75,
            date: '2024-11-15T14:22:00.000Z'
          },
          {
            id: 'pay-003',
            amount: 3456.20,
            date: '2024-11-01T09:15:00.000Z'
          },
          {
            id: 'pay-004',
            amount: 2634.80,
            date: '2024-10-15T16:45:00.000Z'
          },
          {
            id: 'pay-005',
            amount: 3102.30,
            date: '2024-10-01T11:20:00.000Z'
          },
          {
            id: 'pay-006',
            amount: 2897.60,
            date: '2024-09-15T13:10:00.000Z'
          },
          {
            id: 'pay-007',
            amount: 3789.45,
            date: '2024-09-01T08:30:00.000Z'
          },
          {
            id: 'pay-008',
            amount: 2543.25,
            date: '2024-08-15T15:55:00.000Z'
          },
          {
            id: 'pay-009',
            amount: 3334.70,
            date: '2024-08-01T12:40:00.000Z'
          },
          {
            id: 'pay-010',
            amount: 2776.90,
            date: '2024-07-15T17:25:00.000Z'
          },
          {
            id: 'pay-011',
            amount: 3567.85,
            date: '2024-07-01T10:05:00.000Z'
          },
          {
            id: 'pay-012',
            amount: 2445.60,
            date: '2024-06-15T14:35:00.000Z'
          }
]

// @ts-expect-error debug
const generateMockBillingResponse = (period: string): Success<Billing> => {
  const monthsCount = parseInt(period);
  const services: BillingService[] = [];

  // Generate services for each month
  for (let i = monthsCount - 1; i >= 0; i--) {
    const date = new Date();
    date.setMonth(date.getMonth() - i);
    const monthStart = new Date(date.getFullYear(), date.getMonth(), 1);

    const monthServices: BillingService[] = [
      {
        id: i * 10 + 1,
        type: 'coldWater',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 500 + 300) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'supportion',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 500 + 300) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'hotWater',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 800 + 600) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'electricity',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 1200 + 800) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'overhaul',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 400 + 200) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'heating',
        createdAt: monthStart.toISOString().split('T')[0],
        amount:
          date.getMonth() >= 4 && date.getMonth() <= 8
            ? 0
            : Math.round((Math.random() * 3000 + 2000) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
      {
        id: i * 10 + 1,
        type: 'maintenance',
        createdAt: monthStart.toISOString().split('T')[0],
        amount: Math.round((Math.random() * 300 + 200) * 100) / 100,
        status: i > 1 ? 'paid' : 'waiting_for_payment',
      },
    ];

    services.push(...monthServices);
  }

  const utilityConfig = {
    coldWater: { name: 'Холодное водоснабжение', color: 'blue' },
    hotWater: { name: 'Горячее водоснабжение', color: 'red' },
    electricity: { name: 'Электроэнергия', color: 'yellow' },
    heating: { name: 'Отопление', color: 'red' },
    supportion: { name: 'Водоотведение', color: 'orange' },
    maintenance: { name: 'Содержание жилья', color: 'gray' },
    overhaul: { name: 'Капитальный ремонт', color: 'teal' },
  };
  type TotalService = {
    type: 'coldWater' | 'hotWater' | 'electricity' | 'gas' | 'heating' | 'waste' | 'maintenance';
    amount: number;
  };

  const totalServices: TotalService[] = Object.keys(utilityConfig).map((type) => ({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    type: type as any,
    amount:
      Math.round(
        services.filter((s) => s.type === type).reduce((sum, s) => sum + s.amount, 0) * 100
      ) / 100,
  }));

  const totalAmount = Math.round(services.reduce((sum, s) => sum + s.amount, 0) * 100) / 100;

  return {
    success: true,
    data: {
      services,
      total: {
        // @ts-expect-error debug
        services: totalServices,
        amount: totalAmount,
      },
    },
  };
};

export const authApi = {
  getCurrentUser: async (): Promise<Success<User>> => {
    /* return { success: true, data: { id: '1', email: 'test@mail.ru' } }; */

    const response = await fetch(`${BACKEND_URL}/api/me`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Unauthorized');
      }
      throw new Error('Failed to fetch user');
    }

    return response.json();
  },

  signUp: async (email: string, password: string, name: string, sex: number, description: string): Promise<Success> => {
    const response = await fetch(`${BACKEND_URL}/api/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password, name, sex, description }),
    });

    if (!response.ok) {
      throw new Error('Register failed');
    }

    return response.json();
  },

  signIn: async (email: string, password: string): Promise<Success<User>> => {
    const response = await fetch(`${BACKEND_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  },

  logout: async (): Promise<Success> => {
    const response = await fetch(`${BACKEND_URL}/api/logout`, {
      method: 'POST',
      credentials: 'include',
    });

    return response.json();
  },
};

export const accountsApi = {
  getAccounts: async (): Promise<Success<Account[]>> => {
    /* return { */
    /*   success: true, */
    /*   data: [ */
    /*     { */
    /*       id: 1, */
    /*       number: '1234567890', */
    /*       address: 'г. Москва, ул. Ленина, д. 15, кв. 42', */
    /*       ownerFullName: 'Иван Петрович Сидоров', */
    /*       propertySquare: 65.5, */
    /*       residentsCount: 3, */
    /*       isActive: true, */
    /*       companyName: 'ООО "Рога и Копыта"', */
    /*     }, */
    /*     { */
    /*       id: 2, */
    /*       number: '0987654321', */
    /*       address: 'г. Санкт-Петербург, пр. Невский, д. 100', */
    /*       ownerFullName: 'Мария Александровна Иванова', */
    /*       propertySquare: 45.2, */
    /*       residentsCount: 2, */
    /*       isActive: false, */
    /*       companyName: 'ИП Иванова М.А.', */
    /*     }, */
    /*     { */
    /*       id: 3, */
    /*       number: '5555555555', */
    /*       address: 'г. Казань, ул. Баумана, д. 30, кв. 15', */
    /*       ownerFullName: 'Алексей Николаевич Петров', */
    /*       propertySquare: 78.0, */
    /*       residentsCount: 4, */
    /*       isActive: false, */
    /*       companyName: 'ЗАО "Энергострой"', */
    /*     }, */
    /*   ], */
    /* }; */
    const response = await fetch(`${BACKEND_URL}/api/accounts`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch accounts');
    }

    return response.json();
  },
  createAccount: async (account: CreateAccount): Promise<Success<Account>> => {
    const response = await fetch(`${BACKEND_URL}/api/accounts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(account),
    });

    if (!response.ok) {
      throw new Error('Failed to create account');
    }

    return response.json();
  },

  updateAccount: async (accountId: number, isActive: boolean): Promise<Success<Account>> => {
    const response = await fetch(`${BACKEND_URL}/api/accounts/${accountId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ isActive}),
    });

    if (!response.ok) {
      throw new Error('Failed to update account');
    }

    return response.json();
  },

  deleteAccount: async (accountId: number): Promise<Success<Account>> => {
    const response = await fetch(`${BACKEND_URL}/api/accounts/${accountId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to create account');
    }

    return response.json();
  },
};

export const billingsApi = {
  getBillings: async (accountId: string, period: number): Promise<Success<Billing>> => {
    const response = await fetch(
      `${BACKEND_URL}/api/billings?account=${accountId}&period=${period}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch billings');
    }

    return response.json();
  },
};

export const paymentApi = {
  pay: async (
    accountId: number,
    billingIds: number[],
    amount: number,
    creditCard?: { cardNumber: string }
  ): Promise<Success> => {
    const response = await fetch(`${BACKEND_URL}/api/payments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ account_id: accountId, billing_ids: billingIds, amount, creditCard }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch billings');
    }

    return response.json();
  },

  paymentHistory: async (accountId: string): Promise<Success<Payment[]>> => {
    const response = await fetch(`${BACKEND_URL}/api/payments/${accountId}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch payment history');
    }

    return response.json();
  },
};

export const reportsApi = {
  getReport: async (accountId: number, period: number): Promise<Success> => {
    const response = await fetch(
      `${BACKEND_URL}/api/reports/receipt?accountId=${accountId}&period=${period}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch report');
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `report_${accountId}_${period}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    return { success: true, data: undefined };
  },
};

export const tasksApi = {
  getUserTasks: async (userId: number): Promise<Success> => {
    const response = await fetch(`http://localhost:3011/api/tasks?userId=${userId}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }

    return response.json();
  }
}
