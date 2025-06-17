-- Table for accounts
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL UNIQUE,          -- Account number (e.g., ACC001)
    address TEXT NOT NULL,               -- Account address
    area REAL NOT NULL,                  -- Area in square meters
    residents INTEGER NOT NULL,          -- Number of residents
    management_company TEXT NOT NULL,    -- Management company name
    user_id INTEGER NOT NULL             -- User ID (owner/tenant)
);

-- Table for charges
CREATE TABLE IF NOT EXISTS charges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,         -- References accounts(id)
    period_start TEXT NOT NULL,          -- 'YYYY-MM-01'
    period_end TEXT NOT NULL,            -- 'YYYY-MM-30'
    service_type TEXT NOT NULL,          -- e.g., 'water', 'gas', 'electricity'
    amount REAL NOT NULL,                -- Amount for this service
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Table for payments
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,         -- References accounts(id)
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount REAL NOT NULL,               -- Payment amount
    method TEXT NOT NULL,               -- e.g., 'card', 'bank_transfer'
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Table for reports
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,         -- References accounts(id)
    period_start TEXT NOT NULL,          -- 'YYYY-MM-01'
    period_end TEXT NOT NULL,            -- 'YYYY-MM-30'
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,          -- Total amount due
    services_data TEXT NOT NULL,         -- JSON string with service details
    qr_data TEXT,                       -- QR code data (e.g., 'account_id:total_amount')
    file_path TEXT NOT NULL,            -- Path to PDF file
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Insert sample data for accounts
INSERT INTO accounts (number, address, area, residents, management_company, user_id) VALUES
('ACC001', '123 Main St, City', 50.0, 2, 'City Management', 1),
('ACC002', '456 Oak St, City', 60.0, 3, 'City Management', 2),
('ACC003', '789 Pine St, City', 55.0, 2, 'City Management', 3),
('ACC004', '101 Maple St, City', 70.0, 4, 'City Management', 4),
('ACC005', '202 Birch St, City', 65.0, 3, 'City Management', 5);

-- Insert sample data for charges
INSERT INTO charges (account_id, period_start, period_end, service_type, amount) VALUES
(1, '2025-06-01', '2025-06-30', 'water', 500.0),
(1, '2025-06-01', '2025-06-30', 'gas', 500.0),
(1, '2025-06-01', '2025-06-30', 'electricity', 500.0),
(2, '2025-06-01', '2025-06-30', 'water', 800.0),
(2, '2025-06-01', '2025-06-30', 'gas', 800.0),
(2, '2025-06-01', '2025-06-30', 'electricity', 700.0),
(3, '2025-06-01', '2025-06-30', 'water', 600.0),
(3, '2025-06-01', '2025-06-30', 'gas', 600.0),
(3, '2025-06-01', '2025-06-30', 'electricity', 600.0),
(4, '2025-06-01', '2025-06-30', 'water', 700.0),
(4, '2025-06-01', '2025-06-30', 'gas', 700.0),
(4, '2025-06-01', '2025-06-30', 'electricity', 700.0),
(5, '2025-06-01', '2025-06-30', 'water', 650.0),
(5, '2025-06-01', '2025-06-30', 'gas', 650.0),
(5, '2025-06-01', '2025-06-30', 'electricity', 650.0);

-- Insert sample data for payments
INSERT INTO payments (account_id, payment_date, amount, method) VALUES
(1, '2025-06-15 10:00:00', 1000.0, 'card'),
(2, '2025-06-16 12:00:00', 1500.0, 'bank_transfer');

-- Insert sample data for reports
INSERT INTO reports (account_id, period_start, period_end, total_amount, services_data, qr_data, file_path) VALUES
(1, '2025-06-01', '2025-06-30', 1500.0, '{"water":500,"gas":500,"electricity":500}', '1:1500.0', 'receipts/ACC001_202506.pdf'),
(2, '2025-06-01', '2025-06-30', 2300.0, '{"water":800,"gas":800,"electricity":700}', '2:2300.0', 'receipts/ACC002_202506.pdf'),
(3, '2025-06-01', '2025-06-30', 1800.0, '{"water":600,"gas":600,"electricity":600}', '3:1800.0', 'receipts/ACC003_202506.pdf'),
(4, '2025-06-01', '2025-06-30', 2100.0, '{"water":700,"gas":700,"electricity":700}', '4:2100.0', 'receipts/ACC004_202506.pdf'),
(5, '2025-06-01', '2025-06-30', 1950.0, '{"water":650,"gas":650,"electricity":650}', '5:1950.0', 'receipts/ACC005_202506.pdf');