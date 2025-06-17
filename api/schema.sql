CREATE TABLE IF NOT EXISTS api_logs (
    account_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    path         TEXT    NOT NULL,
    method       TEXT    NOT NULL,
    status_code  INTEGER NOT NULL,
    account_id      INTEGER,
    ip_address   TEXT,
    duration_ms  INTEGER,
    user_agent   TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
