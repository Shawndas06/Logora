CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bills (account_id, amount, status, type, created_at) VALUES
-- December 2024 bills (paid)
(2, 659.67, 'paid', 'coldWater', '2024-12-31 00:00:00'),
(2, 623.4, 'paid', 'supportion', '2024-12-31 00:00:00'),
(2, 709.53, 'paid', 'hotWater', '2024-12-31 00:00:00'),
(2, 1995.52, 'paid', 'electricity', '2024-12-31 00:00:00'),
(2, 481.55, 'paid', 'overhaul', '2024-12-31 00:00:00'),
(2, 3245.87, 'paid', 'heating', '2024-12-31 00:00:00'),
(2, 347.56, 'paid', 'maintenance', '2024-12-31 00:00:00'),

-- January 2025 bills (paid)
(2, 705.95, 'paid', 'coldWater', '2025-01-31 00:00:00'),
(2, 327.64, 'paid', 'supportion', '2025-01-31 00:00:00'),
(2, 1043.35, 'paid', 'hotWater', '2025-01-31 00:00:00'),
(2, 1737.65, 'paid', 'electricity', '2025-01-31 00:00:00'),
(2, 371.6, 'paid', 'overhaul', '2025-01-31 00:00:00'),
(2, 4205.74, 'paid', 'heating', '2025-01-31 00:00:00'),
(2, 465.68, 'paid', 'maintenance', '2025-01-31 00:00:00'),

-- February 2025 bills (paid)
(2, 546.82, 'paid', 'coldWater', '2025-02-28 00:00:00'),
(2, 451.51, 'paid', 'supportion', '2025-02-28 00:00:00'),
(2, 1325.13, 'paid', 'hotWater', '2025-02-28 00:00:00'),
(2, 1162.41, 'paid', 'electricity', '2025-02-28 00:00:00'),
(2, 528.82, 'paid', 'overhaul', '2025-02-28 00:00:00'),
(2, 3675.95, 'paid', 'heating', '2025-02-28 00:00:00'),
(2, 425.8, 'paid', 'maintenance', '2025-02-28 00:00:00'),

-- March 2025 bills (paid)
(2, 793.6, 'paid', 'coldWater', '2025-03-31 00:00:00'),
(2, 408.46, 'paid', 'supportion', '2025-03-31 00:00:00'),
(2, 1028.42, 'paid', 'hotWater', '2025-03-31 00:00:00'),
(2, 1194.58, 'paid', 'electricity', '2025-03-31 00:00:00'),
(2, 556.28, 'paid', 'overhaul', '2025-03-31 00:00:00'),
(2, 4552.33, 'paid', 'heating', '2025-03-31 00:00:00'),
(2, 279.18, 'paid', 'maintenance', '2025-03-31 00:00:00'),

-- April 2025 bills (waiting for payment)
(2, 386.96, 'waiting_for_payment', 'coldWater', '2025-04-30 00:00:00'),
(2, 720.16, 'waiting_for_payment', 'supportion', '2025-04-30 00:00:00'),
(2, 1249.07, 'waiting_for_payment', 'hotWater', '2025-04-30 00:00:00'),
(2, 1326.59, 'waiting_for_payment', 'electricity', '2025-04-30 00:00:00'),
(2, 224.42, 'waiting_for_payment', 'overhaul', '2025-04-30 00:00:00'),
(2, 0, 'waiting_for_payment', 'heating', '2025-04-30 00:00:00'),
(2, 217.16, 'waiting_for_payment', 'maintenance', '2025-04-30 00:00:00'),

-- May 2025 bills (waiting for payment)
(2, 507.5, 'waiting_for_payment', 'coldWater', '2025-05-31 00:00:00'),
(2, 507.01, 'waiting_for_payment', 'supportion', '2025-05-31 00:00:00'),
(2, 860.29, 'waiting_for_payment', 'hotWater', '2025-05-31 00:00:00'),
(2, 923.9, 'waiting_for_payment', 'electricity', '2025-05-31 00:00:00'),
(2, 212.38, 'waiting_for_payment', 'overhaul', '2025-05-31 00:00:00'),
(2, 0, 'waiting_for_payment', 'heating', '2025-05-31 00:00:00'),
(2, 290.49, 'waiting_for_payment', 'maintenance', '2025-05-31 00:00:00');

