import {
  Badge,
  Box,
  Button,
  Card,
  Container,
  Divider,
  FileInput,
  Group,
  Modal,
  Rating,
  ScrollArea,
  Select,
  SimpleGrid,
  Stack,
  Tabs,
  Text,
  Textarea,
  TextInput,
  ThemeIcon,
  Timeline,
  Title,
} from '@mantine/core';
import {
  IconAlertTriangle,
  IconArrowDown,
  IconArrowUp,
  IconBolt,
  IconCamera,
  IconCheck,
  IconCircleCheck,
  IconClipboardList,
  IconDotsCircleHorizontal,
  IconDroplet,
  IconElevator,
  IconEye,
  IconFileText,
  IconMinus,
  IconPaperclip,
  IconPlaylistAdd,
  IconPlus,
  IconSparkles,
  IconTool,
  IconUserCheck,
  IconVideo,
} from '@tabler/icons-react';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

// Types
type CategoryType = 'plumbing' | 'electricity' | 'cleaning' | 'elevator' | 'other';
type StatusType =
  | 'created'
  | 'accepted'
  | 'in_work'
  | 'assigned'
  | 'in_progress'
  | 'completed'
  | 'confirmed'
  | 'closed';
type PriorityType = 'low' | 'medium' | 'high' | 'alert';

type Assignee = {
  id: string;
  name: string;
  role: string;
};

type Attachment = {
  type: string;
  url: string;
};

type HistoryItem = {
  timestamp: string;
  action: string;
  user: string;
};

type Request = {
  id: number;
  number: string;
  accountId: string;
  category: CategoryType;
  priority: PriorityType;
  title: string;
  description: string;
  status: StatusType;
  createdAt: string;
  assignee: Assignee | null;
  attachments: Attachment[];
  history: HistoryItem[];
};

type CreateRequestFormData = {
  title: string;
  description: string;
  category: CategoryType;
  priority: PriorityType;
  attachments: Attachment[];
};

type ConfirmCompletionFormData = {
  rating: number;
  comment: string;
};

type CategoryConfig = {
  value: CategoryType;
  label: string;
  icon: React.ComponentType<{ size?: number }>;
  color: string;
};

type StatusConfig = {
  label: string;
  color: string;
  icon: React.ComponentType<{ size?: number }>;
};

type PriorityConfig = {
  label: string;
  color: string;
  icon: React.ComponentType<{ size?: number }>;
};

// Mock data
const mockRequests: Request[] = [
  {
    id: 1,
    number: 'TASK-2025-001234',
    accountId: '1234567890',
    category: 'plumbing',
    priority: 'high',
    title: 'Течет кран на кухне',
    description:
      'Постоянно капает вода из крана. Необходимо заменить прокладку или весь кран полностью. Проблема возникла два дня назад.',
    status: 'in_progress',
    createdAt: '2025-06-17T10:30:00Z',
    assignee: {
      id: 'emp-456',
      name: 'Иванов И.И.',
      role: 'plumber',
    },
    attachments: [
      {
        type: 'image',
        url: '/uploads/photo1.jpg',
      },
      {
        type: 'image',
        url: '/uploads/photo2.jpg',
      },
    ],
    history: [
      {
        timestamp: '2025-06-17T10:30:00Z',
        action: 'created',
        user: 'Петров П.П.',
      },
      {
        timestamp: '2025-06-17T11:15:00Z',
        action: 'accepted',
        user: 'Диспетчер',
      },
      {
        timestamp: '2025-06-17T14:20:00Z',
        action: 'assigned',
        user: 'Иванов И.И.',
      },
    ],
  },
  {
    id: 2,
    number: 'TASK-2025-001235',
    accountId: '1234567890',
    category: 'electricity',
    priority: 'medium',
    title: 'Не работает розетка в кухне',
    description: 'Розетка возле плиты не подает электричество. Возможно проблема с проводкой.',
    status: 'completed',
    createdAt: '2025-06-10T09:15:00Z',
    assignee: {
      id: 'emp-789',
      name: 'Петров П.П.',
      role: 'electrician',
    },
    attachments: [
      {
        type: 'image',
        url: '/uploads/photo3.jpg',
      },
    ],
    history: [
      {
        timestamp: '2025-06-10T09:15:00Z',
        action: 'created',
        user: 'Сидоров С.С.',
      },
      {
        timestamp: '2025-06-10T10:30:00Z',
        action: 'accepted',
        user: 'Диспетчер',
      },
      {
        timestamp: '2025-06-11T08:00:00Z',
        action: 'assigned',
        user: 'Петров П.П.',
      },
      {
        timestamp: '2025-06-12T16:45:00Z',
        action: 'completed',
        user: 'Петров П.П.',
      },
    ],
  },
  {
    id: 3,
    number: 'TASK-2025-001236',
    accountId: '1234567890',
    category: 'cleaning',
    priority: 'low',
    title: 'Уборка подъезда',
    description: 'Необходима генеральная уборка подъезда после ремонтных работ.',
    status: 'created',
    createdAt: '2025-06-17T08:00:00Z',
    assignee: null,
    attachments: [],
    history: [
      {
        timestamp: '2025-06-17T08:00:00Z',
        action: 'created',
        user: 'Смирнов А.А.',
      },
    ],
  },
];

const categories: CategoryConfig[] = [
  { value: 'plumbing', label: 'Сантехника', icon: IconDroplet, color: 'blue' },
  { value: 'electricity', label: 'Электрика', icon: IconBolt, color: 'orange' },
  { value: 'cleaning', label: 'Уборка', icon: IconSparkles, color: 'green' },
  { value: 'elevator', label: 'Лифт', icon: IconElevator, color: 'violet' },
  { value: 'other', label: 'Другое', icon: IconDotsCircleHorizontal, color: 'gray' },
];

const statusConfig: Record<StatusType, StatusConfig> = {
  created: { label: 'Создано', color: 'gray', icon: IconPlaylistAdd },
  accepted: { label: 'Принято', color: 'blue', icon: IconCheck },
  in_work: { label: 'В работе', color: 'cyan', icon: IconTool },
  assigned: { label: 'Назначено', color: 'indigo', icon: IconUserCheck },
  in_progress: { label: 'Выполняется', color: 'blue', icon: IconTool },
  completed: { label: 'Ожидает подтверждения', color: 'orange', icon: IconCheck },
  confirmed: { label: 'Подтверждено', color: 'teal', icon: IconCircleCheck },
  closed: { label: 'Закрыто', color: 'green', icon: IconCircleCheck },
};

const priorityConfig: Record<PriorityType, PriorityConfig> = {
  low: { label: 'Низкий', color: 'green', icon: IconArrowDown },
  medium: { label: 'Средний', color: 'yellow', icon: IconMinus },
  high: { label: 'Высокий', color: 'red', icon: IconArrowUp },
  alert: { label: 'Критический', color: 'red', icon: IconAlertTriangle },
};

type CreateRequestFormProps = {
  opened: boolean;
  onClose: () => void;
  onSubmit: (data: CreateRequestFormData) => void;
};

const CreateRequestForm = ({ opened, onClose, onSubmit }: CreateRequestFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<CreateRequestFormData>({
    defaultValues: {
      title: '',
      description: '',
      category: 'other',
      priority: 'medium',
      attachments: [],
    },
  });

  const onFormSubmit = (data: CreateRequestFormData) => {
    onSubmit(data);
    reset();
    onClose();
  };

  const categoryData = categories.map((cat) => ({
    value: cat.value,
    label: cat.label,
  }));

  const priorityData = [
    { value: 'low', label: 'Низкий' },
    { value: 'medium', label: 'Средний' },
    { value: 'high', label: 'Высокий' },
    { value: 'alert', label: 'Критический' },
  ];

  return (
    <Modal opened={opened} onClose={onClose} title="Создать заявку" size="md">
      <Stack gap="md">
        <TextInput
          label="Название проблемы"
          placeholder="Опишите проблему кратко"
          {...register('title', { required: 'Поле обязательно для заполнения' })}
          error={errors.title?.message}
        />

        <Textarea
          label="Описание проблемы"
          placeholder="Подробно опишите проблему"
          {...register('description', { required: 'Поле обязательно для заполнения' })}
          minRows={4}
          error={errors.description?.message}
        />

        <Select
          label="Категория"
          placeholder="Выберите категорию"
          data={categoryData}
          {...register('category', { required: 'Выберите категорию' })}
          onChange={(value) => setValue('category', value as CategoryType)}
          error={errors.category?.message}
        />

        <Select
          label="Приоритет"
          data={priorityData}
          defaultValue="medium"
          onChange={(value) => setValue('priority', value as PriorityType)}
        />

        <Stack gap="xs">
          <Text size="sm" fw={500}>
            Прикрепить файлы
          </Text>
          <Group gap="xs">
            <FileInput
              placeholder="Выберите фото"
              leftSection={<IconCamera size={16} />}
              accept="image/*"
              multiple
              size="xs"
              flex={1}
            />
            <FileInput
              placeholder="Выберите видео"
              leftSection={<IconVideo size={16} />}
              accept="video/*"
              multiple
              size="xs"
              flex={1}
            />
            <FileInput
              placeholder="Другие файлы"
              leftSection={<IconPaperclip size={16} />}
              multiple
              size="xs"
              flex={1}
            />
          </Group>
        </Stack>

        <Group justify="flex-end" gap="sm">
          <Button variant="default" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit(onFormSubmit)}>Создать заявку</Button>
        </Group>
      </Stack>
    </Modal>
  );
};

type RequestDetailsModalProps = {
  opened: boolean;
  onClose: () => void;
  request: Request;
};

const RequestDetailsModal = ({ opened, onClose, request }: RequestDetailsModalProps) => {
  const category = categories.find((c) => c.value === request.category);
  const statusInfo = statusConfig[request.status];
  const priorityInfo = priorityConfig[request.priority];

  const IconComponent = category?.icon || IconDotsCircleHorizontal;
  const PriorityIcon = priorityInfo?.icon || IconMinus;

  return (
    <Modal opened={opened} onClose={onClose} title="Детали заявки" size="lg">
      <ScrollArea.Autosize mah={600}>
        <Stack gap="lg">
          {/* Header */}
          <Group justify="space-between" align="flex-start">
            <Group gap="md" align="flex-start">
              <ThemeIcon size="xl" variant="filled" color={category?.color || 'gray'}>
                <IconComponent size={24} />
              </ThemeIcon>
              <Box>
                <Title order={3} mb={4}>
                  {request.title}
                </Title>
                <Text size="sm" c="dimmed">
                  {request.number}
                </Text>
              </Box>
            </Group>

            <Group gap="xs">
              <Badge
                color={priorityInfo.color}
                leftSection={<PriorityIcon size={12} />}
                variant="light"
                size="lg"
              >
                {priorityInfo.label}
              </Badge>
              <Badge
                color={statusInfo.color}
                leftSection={<statusInfo.icon size={12} />}
                variant="light"
                size="lg"
              >
                {statusInfo.label}
              </Badge>
            </Group>
          </Group>

          <Divider />

          {/* Description */}
          <Box>
            <Text fw={500} mb="xs">
              Описание:
            </Text>
            <Text c="dimmed">{request.description}</Text>
          </Box>

          {/* Details Grid */}
          <SimpleGrid cols={2} spacing="md">
            <Box>
              <Text size="sm" fw={500} c="dimmed">
                Номер счета
              </Text>
              <Text>{request.accountId}</Text>
            </Box>
            <Box>
              <Text size="sm" fw={500} c="dimmed">
                Категория
              </Text>
              <Text>{category?.label}</Text>
            </Box>
            <Box>
              <Text size="sm" fw={500} c="dimmed">
                Создано
              </Text>
              <Text>{new Date(request.createdAt).toLocaleString('ru-RU')}</Text>
            </Box>
            <Box>
              <Text size="sm" fw={500} c="dimmed">
                Исполнитель
              </Text>
              <Text>
                {request.assignee
                  ? `${request.assignee.name}`
                  : 'Не назначен'}
              </Text>
            </Box>
          </SimpleGrid>

          {/* Attachments */}
          {request.attachments.length > 0 && (
            <>
              <Divider />
              <Box>
                <Text fw={500} mb="md">
                  Вложения ({request.attachments.length}):
                </Text>
                <Group gap="sm">
                  {request.attachments.map((attachment, index) => (
                    <Card key={index} padding="xs" withBorder>
                      <Group gap="xs" align="center">
                        <IconPaperclip size={16} />
                        <Text size="sm">{attachment.type}</Text>
                      </Group>
                    </Card>
                  ))}
                </Group>
              </Box>
            </>
          )}

          {/* History */}
          <Divider />
          <Box>
            <Text fw={500} mb="md">
              История действий:
            </Text>
            <Timeline active={request.history.length - 1} bulletSize={24} lineWidth={2}>
              {request.history.map((item, index) => (
                <Timeline.Item
                  key={index}
                  bullet={<IconFileText size={12} />}
                  title={item.action.charAt(0).toUpperCase() + item.action.slice(1)}
                >
                  <Text c="dimmed" size="sm">
                    {item.user}
                  </Text>
                  <Text size="xs" c="dimmed">
                    {new Date(item.timestamp).toLocaleString('ru-RU')}
                  </Text>
                </Timeline.Item>
              ))}
            </Timeline>
          </Box>
        </Stack>
      </ScrollArea.Autosize>
    </Modal>
  );
};

type ConfirmCompletionModalProps = {
  opened: boolean;
  onClose: () => void;
  onConfirm: (data: ConfirmCompletionFormData) => void;
  request: Request;
};

const ConfirmCompletionModal = ({
  opened,
  onClose,
  onConfirm,
  request,
}: ConfirmCompletionModalProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<ConfirmCompletionFormData>({
    defaultValues: {
      rating: 0,
      comment: '',
    },
  });

  const rating = watch('rating');

  const onFormSubmit = (data: ConfirmCompletionFormData) => {
    onConfirm(data);
    reset();
    onClose();
  };

  return (
    <Modal opened={opened} onClose={onClose} title="Подтвердить выполнение" size="md">
      <Stack gap="md">
        <Text size="sm" c="dimmed" mb="md">
          Заявка: {request.title}
        </Text>

        <Box>
          <Text size="sm" fw={500} mb="xs">
            Оценить качество работы *
          </Text>
          <Rating value={rating} onChange={(value) => setValue('rating', value)} size="lg" />
          {errors.rating && (
            <Text size="xs" c="red" mt="xs">
              Пожалуйста, поставьте оценку
            </Text>
          )}
        </Box>

        <Textarea
          label="Комментарий к работе"
          placeholder="Оставьте комментарий о качестве выполненной работы"
          {...register('comment', { required: 'Пожалуйста, оставьте комментарий' })}
          minRows={3}
          error={errors.comment?.message}
        />

        <Group justify="flex-end" gap="sm">
          <Button variant="default" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={handleSubmit(onFormSubmit)} disabled={!rating || rating === 0}>
            Подтвердить выполнение
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};

type RequestCardProps = {
  request: Request;
  onConfirmCompletion: (request: Request) => void;
  onViewDetails: (request: Request) => void;
};

const RequestCard = ({ request, onConfirmCompletion, onViewDetails }: RequestCardProps) => {
  const category = categories.find((c) => c.value === request.category);
  const statusInfo = statusConfig[request.status];
  const priorityInfo = priorityConfig[request.priority];

  const IconComponent = category?.icon || IconDotsCircleHorizontal;
  const PriorityIcon = priorityInfo?.icon || IconMinus;

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder mb="md" style={{ cursor: 'pointer' }}>
      <Stack gap="md">
        <Group justify="space-between" align="flex-start">
          <Group
            gap="md"
            align="flex-start"
            onClick={() => onViewDetails(request)}
            style={{ flex: 1 }}
          >
            <Group>
              <ThemeIcon size="lg" variant="filled" color={category?.color || 'gray'}>
                <IconComponent size={20} />
              </ThemeIcon>
              <Text size="sm" c="dimmed" ta="left">
                {request.number}
              </Text>
            </Group>
          </Group>

          <Group gap="xs">
            <Badge
              color={priorityInfo.color}
              leftSection={<PriorityIcon size={12} />}
              variant="light"
              size="sm"
            >
              {priorityInfo.label}
            </Badge>
            <Badge
              color={statusInfo.color}
              leftSection={<statusInfo.icon size={12} />}
              variant="light"
              size="sm"
            >
              {statusInfo.label}
            </Badge>
          </Group>
        </Group>

        <Box ta="left">
          <Title order={4} mb={4}>
            {request.title}
          </Title>

          <Text
            size="sm"
            c="dimmed"
            onClick={() => onViewDetails(request)}
            style={{ cursor: 'pointer' }}
          >
            {request.description.length > 150
              ? `${request.description.substring(0, 150)}...`
              : request.description}
          </Text>
        </Box>

        <Divider />

        <Group justify="space-between" align="center">
          <Group gap="md">
            <Text size="xs" c="dimmed">
              Создано: {new Date(request.createdAt).toLocaleDateString('ru-RU')}
            </Text>
            {request.assignee && (
              <Text size="xs" c="dimmed">
                Исполнитель: {request.assignee.name}
              </Text>
            )}
          </Group>

          <Group gap="xs" align="center">
            <Button
              variant="subtle"
              size="xs"
              leftSection={<IconEye size={14} />}
              onClick={(e) => {
                e.stopPropagation();
                onViewDetails(request);
              }}
            >
              Подробнее
            </Button>
            {request.attachments.length > 0 && (
              <Group gap="xs" align="center">
                <IconPaperclip size={16} color="var(--mantine-color-gray-6)" />
                <Text size="xs" c="dimmed">
                  {request.attachments.length}
                </Text>
              </Group>
            )}
          </Group>
        </Group>

        {request.status === 'completed' && (
          <>
            <Divider />
            <Group justify="center">
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  onConfirmCompletion(request);
                }}
                leftSection={<IconCheck size={16} />}
                color="green"
              >
                Подтвердить выполнение
              </Button>
            </Group>
          </>
        )}
      </Stack>
    </Card>
  );
};

type StatCardProps = {
  title: string;
  value: number;
  icon: React.ComponentType<{ size?: number }>;
  color: string;
};

const StatCard = ({ title, value, icon: Icon, color }: StatCardProps) => (
  <Card shadow="sm" padding="lg" radius="md" withBorder>
    <Group justify="space-between" align="center">
      <Box>
        <Text size="sm" c="dimmed" mb="xs">
          {title}
        </Text>
        <Title order={2}>{value}</Title>
      </Box>
      <ThemeIcon size="xl" variant="light" color={color}>
        <Icon size={24} />
      </ThemeIcon>
    </Group>
  </Card>
);

type EmptyStateProps = {
  onCreateClick: () => void;
};

const EmptyState = ({ onCreateClick }: EmptyStateProps) => (
  <Container size="md" py="xl">
    <Card shadow="sm" padding="xl" radius="md" withBorder>
      <Stack align="center" gap="md">
        <ThemeIcon size={64} variant="light" color="gray">
          <IconClipboardList size={32} />
        </ThemeIcon>
        <Title order={3} c="dimmed">
          Нет заявок
        </Title>
        <Text c="dimmed" ta="center">
          У вас пока нет созданных заявок. Создайте первую заявку для обслуживания.
        </Text>
        <Button leftSection={<IconPlus size={16} />} onClick={onCreateClick}>
          Создать заявку
        </Button>
      </Stack>
    </Card>
  </Container>
);

export const Orders = () => {
  const [requests, setRequests] = useState<Request[]>(mockRequests);
  const [createModalOpened, setCreateModalOpened] = useState(false);
  const [confirmModalOpened, setConfirmModalOpened] = useState(false);
  const [detailsModalOpened, setDetailsModalOpened] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<Request | null>(null);
  const [activeTab, setActiveTab] = useState<string>('all');

  const handleCreateRequest = (formData: CreateRequestFormData) => {
    const newRequest: Request = {
      id: requests.length + 1,
      number: `TASK-2025-${String(requests.length + 1).padStart(6, '0')}`,
      accountId: '1234567890',
      category: formData.category,
      priority: formData.priority,
      title: formData.title,
      description: formData.description,
      status: 'created',
      createdAt: new Date().toISOString(),
      assignee: null,
      attachments: formData.attachments,
      history: [
        {
          timestamp: new Date().toISOString(),
          action: 'created',
          user: 'Текущий пользователь',
        },
      ],
    };
    setRequests((prev) => [newRequest, ...prev]);
  };

  const handleConfirmCompletion = (request: Request) => {
    setSelectedRequest(request);
    setConfirmModalOpened(true);
  };

  const handleViewDetails = (request: Request) => {
    setSelectedRequest(request);
    setDetailsModalOpened(true);
  };

  const handleConfirmSubmit = (data: ConfirmCompletionFormData) => {
    if (!selectedRequest) return;

    setRequests((prev) =>
      prev.map((req) =>
        req.id === selectedRequest.id
          ? {
              ...req,
              status: 'confirmed' as StatusType,
              history: [
                ...req.history,
                {
                  timestamp: new Date().toISOString(),
                  action: 'confirmed',
                  user: `Текущий пользователь (Оценка: ${data.rating}/5, Комментарий: ${data.comment})`,
                },
              ],
            }
          : req
      )
    );
  };

  const filteredRequests = () => {
    if (activeTab === 'all') return requests;
    return requests.filter((r) => r.status === activeTab);
  };

  const getStatusCounts = () => {
    return {
      all: requests.length,
      created: requests.filter((r) => r.status === 'created').length,
      accepted: requests.filter((r) => r.status === 'accepted').length,
      in_progress: requests.filter((r) => r.status === 'in_progress').length,
      completed: requests.filter((r) => r.status === 'completed').length,
      confirmed: requests.filter((r) => r.status === 'confirmed').length,
      closed: requests.filter((r) => r.status === 'closed').length,
    };
  };

  const statusCounts = getStatusCounts();

  if (requests.length === 0) {
    return (
      <>
        <EmptyState onCreateClick={() => setCreateModalOpened(true)} />
        <CreateRequestForm
          opened={createModalOpened}
          onClose={() => setCreateModalOpened(false)}
          onSubmit={handleCreateRequest}
        />
      </>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Stack gap="xl">
        <Group justify="space-between" align="center">
          <Title order={1}>Заявки на обслуживание</Title>
          <Button leftSection={<IconPlus size={16} />} onClick={() => setCreateModalOpened(true)}>
            Создать заявку
          </Button>
        </Group>

        <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="lg">
          <StatCard
            title="Всего заявок"
            value={statusCounts.all}
            icon={IconClipboardList}
            color="blue"
          />
          <StatCard
            title="Создано"
            value={statusCounts.created}
            icon={IconPlaylistAdd}
            color="gray"
          />
          <StatCard
            title="В работе"
            value={statusCounts.in_progress}
            icon={IconTool}
            color="blue"
          />
          <StatCard
            title="Подтверждено"
            value={statusCounts.confirmed}
            icon={IconCircleCheck}
            color="green"
          />
        </SimpleGrid>

        <Tabs value={activeTab} onChange={(v) => setActiveTab(v || 'all')}>
          <Tabs.List>
            <Tabs.Tab value="all">Все ({statusCounts.all})</Tabs.Tab>
            <Tabs.Tab value="created" leftSection={<IconPlaylistAdd size={14} />}>
              Создано ({statusCounts.created})
            </Tabs.Tab>
            <Tabs.Tab value="in_progress" leftSection={<IconTool size={14} />}>
              В работе ({statusCounts.in_progress})
            </Tabs.Tab>
            <Tabs.Tab value="completed" leftSection={<IconCheck size={14} />}>
              Ожидают подтверждения ({statusCounts.completed})
            </Tabs.Tab>
            <Tabs.Tab value="confirmed" leftSection={<IconCircleCheck size={14} />}>
              Подтверждено ({statusCounts.confirmed})
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value={activeTab} pt="lg">
            <Stack gap="md">
              {filteredRequests().map((request) => (
                <RequestCard
                  key={request.id}
                  request={request}
                  onConfirmCompletion={handleConfirmCompletion}
                  onViewDetails={handleViewDetails}
                />
              ))}
            </Stack>
          </Tabs.Panel>
        </Tabs>
      </Stack>

      <CreateRequestForm
        opened={createModalOpened}
        onClose={() => setCreateModalOpened(false)}
        onSubmit={handleCreateRequest}
      />

      {selectedRequest && (
        <>
          <RequestDetailsModal
            opened={detailsModalOpened}
            onClose={() => {
              setDetailsModalOpened(false);
              setSelectedRequest(null);
            }}
            request={selectedRequest}
          />

          <ConfirmCompletionModal
            opened={confirmModalOpened}
            onClose={() => {
              setConfirmModalOpened(false);
              setSelectedRequest(null);
            }}
            onConfirm={handleConfirmSubmit}
            request={selectedRequest}
          />
        </>
      )}
    </Container>
  );
};
