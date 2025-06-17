    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

INSERT INTO bills (account_id, amount, status, type, created_at) VALUES
-- April 2025 bills (waiting for payment)
(3, 386.96, 'waiting_for_payment', 'coldWater', '2025-04-30 00:00:00'),
(3, 720.16, 'waiting_for_payment', 'supportion', '2025-04-30 00:00:00'),
(3, 1249.07, 'waiting_for_payment', 'hotWater', '2025-04-30 00:00:00'),
(3, 1326.59, 'waiting_for_payment', 'electricity', '2025-04-30 00:00:00'),
(3, 224.42, 'waiting_for_payment', 'overhaul', '2025-04-30 00:00:00'),
(3, 0, 'waiting_for_payment', 'heating', '2025-04-30 00:00:00'),
(3, 217.16, 'waiting_for_payment', 'maintenance', '2025-04-30 00:00:00'),

-- May 2025 bills (waiting for payment)
(3, 507.5, 'waiting_for_payment', 'coldWater', '2025-05-31 00:00:00'),
(3, 507.01, 'waiting_for_payment', 'supportion', '2025-05-31 00:00:00'),
(3, 860.29, 'waiting_for_payment', 'hotWater', '2025-05-31 00:00:00'),
(3, 923.9, 'waiting_for_payment', 'electricity', '2025-05-31 00:00:00'),
(3, 212.38, 'waiting_for_payment', 'overhaul', '2025-05-31 00:00:00'),
(3, 0, 'waiting_for_payment', 'heating', '2025-05-31 00:00:00'),
(3, 290.49, 'waiting_for_payment', 'maintenance', '2025-05-31 00:00:00'),

-- June 2025 bills (waiting for payment, from user's insert)
(3, 620.75, 'waiting_for_payment', 'coldWater', '2025-06-30 00:00:00'),
(3, 950.20, 'waiting_for_payment', 'electricity', '2025-06-30 00:00:00'),
(3, 310.15, 'waiting_for_payment', 'maintenance', '2025-06-30 00:00:00'),

-- June 2025 additional bills (waiting for payment)
(3, 600.0, 'waiting_for_payment', 'supportion', '2025-06-30 00:00:00'),
(3, 1000.0, 'waiting_for_payment', 'hotWater', '2025-06-30 00:00:00'),
(3, 220.0, 'waiting_for_payment', 'overhaul', '2025-06-30 00:00:00');
