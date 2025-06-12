-- Тестовые пользователи
INSERT INTO users (email, password, full_name, is_active, created_at, is_verified) VALUES
    ('ivan@example.com', 'password123', 'Иван Иванов', 1, CURRENT_TIMESTAMP, 1),
    ('maria@example.com', 'password123', 'Мария Петрова', 1, CURRENT_TIMESTAMP, 1),
    ('alex@example.com', 'password123', 'Алексей Сидоров', 1, CURRENT_TIMESTAMP, 1);

-- Добавление тестовых счетов
INSERT INTO accounts (number, name, address, status) VALUES
('1001', 'Иванов Иван', 'ул. Ленина, 1', 'active'),
('1002', 'Петров Петр', 'ул. Гагарина, 2', 'active'),
('1003', 'Сидоров Сидор', 'ул. Пушкина, 3', 'inactive');

-- Добавление тестовых начислений
INSERT INTO charges (account_id, service, amount, start_date, end_date, status) VALUES
(1, 'Электричество', 1000.00, '2024-01-01', '2024-01-31', 'paid'),
(1, 'Вода', 500.00, '2024-01-01', '2024-01-31', 'pending'),
(2, 'Электричество', 1200.00, '2024-01-01', '2024-01-31', 'paid'),
(2, 'Газ', 800.00, '2024-01-01', '2024-01-31', 'paid'),
(3, 'Электричество', 900.00, '2024-01-01', '2024-01-31', 'pending');

-- Добавление тестовых платежей
INSERT INTO payments (account_id, amount, date, method, receipt, status) VALUES
(1, 1000.00, '2024-01-15 10:00:00', 'card', '20240115-1234', 'completed'),
(2, 1200.00, '2024-01-16 11:00:00', 'cash', '20240116-5678', 'completed'),
(2, 800.00, '2024-01-17 12:00:00', 'card', '20240117-9012', 'completed'); 