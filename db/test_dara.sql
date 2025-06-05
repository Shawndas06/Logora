-- Вставка пользователей
INSERT INTO @@
users (username, password_hash) VALUES ('user1', 'hash1');
INSERT INTO users (username, password_hash) VALUES ('user2', 'hash2');

-- Вставка лицевых счетов
INSERT INTO accounts (user_id, account_number, address) VALUES (1, '12345', 'ул. Ленина, 1');
INSERT INTO accounts (user_id, account_number, address) VALUES (2, '67890', 'ул. Пушкина, 2');

-- Вставка начислений
INSERT INTO charges (account_id, amount, status, date) VALUES (1, 100.0, 'не оплачено', '2023-10-01');
INSERT INTO charges (account_id, amount, status, date) VALUES (1, 150.0, 'оплачено', '2023-11-01');
INSERT INTO charges (account_id, amount, status, date) VALUES (2, 200.0, 'не оплачено', '2023-10-15');

-- Вставка оплат
INSERT INTO payments (charge_id, amount, date) VALUES (2, 150.0, '2023-11-05');