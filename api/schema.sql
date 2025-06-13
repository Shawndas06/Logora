CREATE TABLE IF NOT EXISTS api_logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    path         TEXT    NOT NULL,
    method       TEXT    NOT NULL,
    status_code  INTEGER NOT NULL,
    user_id      INTEGER,
    ip_address   TEXT,
    duration_ms  INTEGER,
    user_agent   TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO api_logs (path, method, status_code, user_id, ip_address, duration_ms, user_agent) VALUES
('/accounts/1', 'GET', 200, 1, '127.0.0.1', 120, 'PostmanRuntime/7.28.4'),
('/accounts/2', 'GET', 200, 2, '127.0.0.1', 130, 'PostmanRuntime/7.28.4'),
('/accounts/3', 'GET', 200, 3, '127.0.0.1', 140, 'PostmanRuntime/7.28.4'),
('/payments/4', 'POST', 500, 4, '127.0.0.1', 500, 'PostmanRuntime/7.28.4'),
('/reports/5', 'GET', 200, 5, '127.0.0.1', 110, 'PostmanRuntime/7.28.4');
