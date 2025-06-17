import sqlite3
from config import DATABASE_PATH

def get_db():
    """Connect to the SQLite database."""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Create tables if not exist."""
    conn = get_db()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                accountId INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                priority TEXT,
                createdAt TEXT NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS executors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS task_assignees (
                task_id INTEGER UNIQUE,
                executor_id INTEGER,
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(executor_id) REFERENCES executors(id)
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                timestamp TEXT,
                message TEXT,
                user TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                filename TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                timestamp TEXT,
                action TEXT,
                user TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                message TEXT,
                point INTEGER,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
        ''')
        conn.commit()
    finally:
        conn.close()
