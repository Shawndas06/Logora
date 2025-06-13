import {
  Button,
  Card,
  Center,
  Group,
  Loader,
  Modal,
  Select,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconFileDownload } from '@tabler/icons-react';
import { reportsApi } from '~/shared/api';

import { useState } from 'react';

type Props = {
  accountId: number;
};

export const ExportReport = ({ accountId }: Props) => {
  const [selectedMonths, setSelectedMonths] = useState<string>('6');
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState<{
    progress: number;
    message: string;
  } | null>(null);
  const [exportComplete, setExportComplete] = useState(false);
  const [opened, setOpened] = useState(false);

  const monthOptions = Array.from({ length: 24 }, (_, i) => ({
    value: (i + 1).toString(),
    label: `${i + 1} ${i === 0 ? 'месяц' : i < 4 ? 'месяца' : 'месяцев'}`,
  }));

  const handleExport = async () => {
    setIsExporting(true);
    setExportProgress(null);
    setExportComplete(false);

    try {
      const steps = [
        { progress: 25, message: 'Подготовка запроса...' },
        { progress: 50, message: 'Обработка данных на сервере...' },
        { progress: 75, message: 'Генерация PDF...' },
        { progress: 100, message: 'Скачивание файла...' },
      ];

      for (const step of steps) {
        setExportProgress(step);
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      await reportsApi.getReport(accountId, parseInt(selectedMonths));

      setExportComplete(true);
      setTimeout(() => {
        setOpened(false);
        setIsExporting(false);
        setExportProgress(null);
        setExportComplete(false);
      }, 1500);

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (_err) {
      setIsExporting(false);
      setExportProgress(null);
          notifications.show({
            title: 'Ошибка',
            message: 'Проблема при экспорте отчёта. Попробуйте позже.',
            color: 'red',
          });
    }
  };

  const handleClose = () => {
    if (!isExporting) {
      setOpened(false);
      setExportProgress(null);
      setExportComplete(false);
    }
  };

  // Calculate filtered payments count for preview
  const currentDate = new Date();
  const filterDate = new Date();
  filterDate.setMonth(currentDate.getMonth() - parseInt(selectedMonths) + 1);
  filterDate.setDate(1);

  return (
    <>
      <Modal
        opened={opened}
        onClose={handleClose}
        title={
          <Group>
            <IconFileDownload size={20} />
            <Title order={4}>Экспорт истории платежей</Title>
          </Group>
        }
        centered
        closeOnClickOutside={!isExporting}
        closeOnEscape={!isExporting}
      >
        <Stack gap="md">
          {!isExporting && !exportComplete && (
            <>
              <Text size="sm" c="dimmed">
                Выберите период для экспорта в PDF
              </Text>

              <Select
                label="Количество месяцев"
                data={monthOptions}
                value={selectedMonths}
                onChange={(value) => setSelectedMonths(value || '6')}
                description="История платежей будет экспортирована за выбранный период"
              />

              <Card withBorder p="sm" bg="blue.0">
                <Group justify="center">
                  <Text size="sm" fw={500}>
                    Экспорт за {selectedMonths}{' '}
                    {parseInt(selectedMonths) === 1
                      ? 'месяц'
                      : parseInt(selectedMonths) < 5
                        ? 'месяца'
                        : 'месяцев'}
                  </Text>
                </Group>
              </Card>

              <Group mt="md">
                <Button variant="subtle" onClick={handleClose} style={{ flex: 1 }}>
                  Отмена
                </Button>
                <Button
                  onClick={handleExport}
                  leftSection={<IconFileDownload size={16} />}
                  style={{ flex: 1 }}
                >
                  Скачать PDF
                </Button>
              </Group>
            </>
          )}

          {isExporting && exportProgress && (
            <Stack gap="md">
              <Center>
                <ThemeIcon size="xl" variant="light" color="blue">
                  <IconFileDownload size={28} />
                </ThemeIcon>
              </Center>

              <Text ta="center" fw={500}>
                {exportProgress.message}
              </Text>
              <Center>
                <Loader size="lg" color="blue" variant="dots" />
              </Center>
            </Stack>
          )}

          {exportComplete && (
            <Stack gap="md" align="center">
              <ThemeIcon size="xl" color="green" variant="light">
                <IconCheck size={28} />
              </ThemeIcon>
              <Text ta="center" fw={500} c="green">
                PDF успешно скачан!
              </Text>
              <Text ta="center" size="sm" c="dimmed">
                Файл сохранен на ваше устройство
              </Text>
            </Stack>
          )}
        </Stack>
      </Modal>
      <Button
        leftSection={<IconFileDownload size={16} />}
        variant="light"
        onClick={() => setOpened(true)}
      >
        Экспорт
      </Button>
    </>
  );
};
