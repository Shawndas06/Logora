CREATE TABLE IF NOT EXISTS payments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id    INTEGER NOT NULL,
    billing_ids   TEXT    NOT NULL,   -- CSV вида "1,2,3"
    amount        REAL    NOT NULL,
    credit_card   TEXT    NOT NULL,   -- номер карты, строкой
    status        TEXT    NOT NULL
                        CHECK (status IN ('PROCESSING','COMPLETED','ERROR')),
    created_at    TEXT    NOT NULL
                        DEFAULT (datetime('now'))
);

INSERT INTO payments (account_id, billing_ids, amount, credit_card, status) VALUES
(1, '1', 1500.0, '4111111111111111', 'COMPLETED'),
(2, '2', 2300.0, '4111111111111111', 'PROCESSING'),
(3, '3', 1800.0, '4111111111111111', 'COMPLETED'),
(4, '4', 2100.0, '4111111111111111', 'ERROR'),
(5, '5', 1950.0, '4111111111111111', 'COMPLETED');
