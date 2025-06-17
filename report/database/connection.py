import sqlite3
from config import Config
from datetime import datetime, timedelta


def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables."""
    conn = get_db()
    try:
        # Create accounts table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            area REAL NOT NULL,
            residents INTEGER NOT NULL,
            management_company TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # Create charges table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS charges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            service_type TEXT NOT NULL,
            amount REAL NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
        ''')

        # Create payments table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            payment_date DATE NOT NULL,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
        ''')

        # Create reports table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            total_amount REAL NOT NULL,
            services_data TEXT NOT NULL,
            qr_data TEXT NOT NULL,
            file_path TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
        ''')

        # Create test data if it doesn't exist
        create_test_data(conn)
        conn.commit()
    finally:
        conn.close()


def create_test_data(conn):
    """Create test data if it doesn't exist."""
    # Check if test account exists
    account = conn.execute("SELECT id FROM accounts WHERE number = 'TEST001'").fetchone()
    if not account:
        # Create test account
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO accounts (number, address, area, residents, management_company)
        VALUES (?, ?, ?, ?, ?)
        ''', ('TEST001', 'ул. Тестовая, д. 1', 50.5, 2, 'ООО "Тестовая УК"'))
        account_id = cursor.lastrowid
        conn.commit()

        # Create test charges
        current_date = datetime.now()
        period_start = current_date.replace(day=1).strftime('%Y-%m-%d')
        period_end = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
        charges = [
            ('Отопление', 1500.0),
            ('Горячая вода', 800.0),
            ('Холодная вода', 300.0),
            ('Электричество', 1200.0),
            ('Вывоз мусора', 200.0)
        ]
        for service_type, amount in charges:
            cursor.execute('''
            INSERT INTO charges (account_id, service_type, amount, period_start, period_end)
            VALUES (?, ?, ?, ?, ?)
            ''', (account_id, service_type, amount, period_start, period_end))

        # Create test payments
        payments = [
            (current_date.strftime('%Y-%m-%d'), 3000.0, 'Банковская карта'),
            ((current_date - timedelta(days=15)).strftime('%Y-%m-%d'), 1000.0, 'Наличные')
        ]
        for payment_date, amount, method in payments:
            cursor.execute('''
            INSERT INTO payments (account_id, payment_date, amount, method)
            VALUES (?, ?, ?, ?)
            ''', (account_id, payment_date, amount, method))
        conn.commit()
        cursor.close()