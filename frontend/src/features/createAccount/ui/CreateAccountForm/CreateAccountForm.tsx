import { zodResolver } from '@hookform/resolvers/zod';
import { Button, Group, Modal, Stack, TextInput } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconBuilding, IconCreditCard, IconUser } from '@tabler/icons-react';
import { z } from 'zod';
import type { CreateAccount } from '~/shared/api';

import { Controller, useForm } from 'react-hook-form';

import { useCreateAccountMutation } from '../../api';

type AccountFormData = CreateAccount;

type Props = {
  opened: boolean;
  onClose: () => void;
};

const accountSchema = z.object({
  number: z
    .string()
    .length(10, 'Номер должен содержать ровно 10 цифр')
    .regex(/^\d+$/, 'Номер должен содержать только цифры'),

  address: z.string().min(5, 'Адрес должен содержать минимум 5 символов'),

  ownerFullName: z
    .string()
    .min(3, 'ФИО должно содержать минимум 3 символа')
    .regex(/^[а-яА-ЯёЁa-zA-Z\s]+$/, 'ФИО должно содержать только буквы и пробелы'),

  propertySquare: z
    .number()
    .min(0.1, 'Площадь должна быть больше 0')
    .max(10000, 'Площадь не может превышать 10000 м²'),

  residentsCount: z
    .number()
    .int('Количество жильцов должно быть целым числом')
    .min(1, 'Количество жильцов должно быть больше 0')
    .max(50, 'Количество жильцов не может превышать 50'),

  companyName: z.string().min(2, 'Название компании должно содержать минимум 2 символа'),
});

export const CreateAccountForm = ({ opened, onClose }: Props) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<AccountFormData>({
    resolver: zodResolver(accountSchema),
    defaultValues: {
      number: '',
      address: '',
      ownerFullName: '',
      propertySquare: 0,
      residentsCount: 0,
      companyName: '',
    },
  });

  const { create, isLoading } = useCreateAccountMutation();

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleCreate = (data: AccountFormData) => {
    create(
      { account: data },
      {
        onSuccess: () => {
          notifications.show({
            title: 'Успешно',
            message: 'Лицевой счёт успешно создан',
            color: 'green',
          });
          reset();
          onClose();
        },
        onError: () => {
          notifications.show({
            title: 'Ошибка',
            message: 'Произошла ошибка при создании лицевого счёта',
            color: 'red',
          });
        },
      }
    );
  };

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title="Добавить новый лицевой счёт"
      centered
      size="md"
    >
      <form onSubmit={handleSubmit(handleCreate)}>
        <Stack gap="md">
          <Controller
            name="number"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Номер лицевого счёта"
                placeholder="Введите 10-значный номер"
                leftSection={<IconCreditCard size={16} />}
                error={errors.number?.message}
                maxLength={10}
              />
            )}
          />

          <Controller
            name="address"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Адрес"
                placeholder="Введите полный адрес"
                leftSection={<IconBuilding size={16} />}
                error={errors.address?.message}
              />
            )}
          />

          <Controller
            name="ownerFullName"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="ФИО владельца"
                placeholder="Введите полное имя"
                leftSection={<IconUser size={16} />}
                error={errors.ownerFullName?.message}
              />
            )}
          />

          <Group grow>
            <Controller
              name="propertySquare"
              control={control}
              render={({ field }) => (
                <TextInput
                  {...field}
                  label="Площадь (м²)"
                  placeholder="0"
                  type="number"
                  step="0.1"
                  min="0"
                  onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                  error={errors.propertySquare?.message}
                />
              )}
            />

            <Controller
              name="residentsCount"
              control={control}
              render={({ field }) => (
                <TextInput
                  {...field}
                  label="Количество жильцов"
                  placeholder="0"
                  type="number"
                  min="0"
                  onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                  error={errors.residentsCount?.message}
                />
              )}
            />
          </Group>

          <Controller
            name="companyName"
            control={control}
            render={({ field }) => (
              <TextInput
                {...field}
                label="Название компании"
                placeholder="Введите название компании"
                leftSection={<IconBuilding size={16} />}
                error={errors.companyName?.message}
              />
            )}
          />

          <Group justify="flex-end" mt="md">
            <Button variant="subtle" onClick={handleClose}>
              Отмена
            </Button>
            <Button type="submit" loading={isLoading}>
              Добавить
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
};
