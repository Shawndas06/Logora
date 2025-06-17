import sqlite3
from config import Config

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize payments table if not exists."""
    conn = get_db()
    try:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id    INTEGER NOT NULL,
            billing_ids   TEXT    NOT NULL,   -- CSV вида "1,2,3"
            amount        REAL    NOT NULL,
            status        TEXT    NOT NULL
                                CHECK (status IN ('PROCESSING','COMPLETED','ERROR')),
            created_at    TEXT    NOT NULL
                                DEFAULT (datetime('now'))
                );
        ''')
        conn.commit()
    finally:
        conn.close()
