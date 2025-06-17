import sqlite3
from config import Config

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize users table if not exists."""
    conn = get_db()
    try:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            is_admin       INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
            email         TEXT    NOT NULL UNIQUE,
            description  TEXT,
            username     TEXT    NOT NULL UNIQUE,
            password      TEXT    NOT NULL,
            name          TEXT    NOT NULL,
            sex           INTEGER NOT NULL CHECK (sex IN (0, 1))
        );
        ''')
        conn.commit()
    finally:
        conn.close()
