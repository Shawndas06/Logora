CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  is_admin       INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
  email         TEXT    NOT NULL UNIQUE,
  description  TEXT,
  username     TEXT    NOT NULL UNIQUE,
  password      TEXT    NOT NULL,
  name          TEXT    NOT NULL,
  sex           INTEGER NOT NULL CHECK
  );
