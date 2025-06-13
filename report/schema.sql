CREATE TABLE IF NOT EXISTS reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id      INTEGER NOT NULL,          -- какой счёт
    period_start    TEXT NOT NULL,             -- 'YYYY-MM-01'
    period_end      TEXT NOT NULL,             -- 'YYYY-MM-30'
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount    REAL NOT NULL,             -- итоговая сумма к оплате
    services_data   TEXT NOT NULL,             -- JSON-строка с детализацией по услугам
    qr_data         TEXT,                      -- данные, на основе которых создаётся QR‑код
    file_path       TEXT NOT NULL              -- путь к PDF‑файлу
);

INSERT INTO reports (account_id, period_start, period_end, total_amount, services_data, qr_data, file_path) VALUES
(1, '2025-06-01', '2025-06-30', 1500.0, '{"water":500,"gas":500,"electricity":500}', 'QRDATA1', '/files/ACC001_202506.pdf'),
(2, '2025-06-01', '2025-06-30', 2300.0, '{"water":800,"gas":800,"electricity":700}', 'QRDATA2', '/files/ACC002_202506.pdf'),
(3, '2025-06-01', '2025-06-30', 1800.0, '{"water":600,"gas":600,"electricity":600}', 'QRDATA3', '/files/ACC003_202506.pdf'),
(4, '2025-06-01', '2025-06-30', 2100.0, '{"water":700,"gas":700,"electricity":700}', 'QRDATA4', '/files/ACC004_202506.pdf'),
(5, '2025-06-01', '2025-06-30', 1950.0, '{"water":650,"gas":650,"electricity":650}', 'QRDATA5', '/files/ACC005_202506.pdf');
