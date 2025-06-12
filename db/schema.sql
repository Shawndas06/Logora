-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы лицевых счетов
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(10) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    area DECIMAL(10,2) NOT NULL,
    residents_count INTEGER NOT NULL,
    management_company VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы услуг
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    unit VARCHAR(20) NOT NULL
);

-- Создание таблицы начислений
CREATE TABLE IF NOT EXISTS charges (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    service_id INTEGER REFERENCES services(id),
    period DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    consumption DECIMAL(10,2),
    rate DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    period DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    receipt_number VARCHAR(20) UNIQUE
);

-- Создание таблицы деталей платежей
CREATE TABLE IF NOT EXISTS payment_details (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id),
    service_id INTEGER REFERENCES services(id),
    amount DECIMAL(10,2) NOT NULL
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_charges_account_id ON charges(account_id);
CREATE INDEX IF NOT EXISTS idx_charges_period ON charges(period);
CREATE INDEX IF NOT EXISTS idx_payments_account_id ON payments(account_id);
CREATE INDEX IF NOT EXISTS idx_payments_period ON payments(period); 