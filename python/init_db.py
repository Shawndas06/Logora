import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        email TEXT
    )
    ''')

    # Create accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        number TEXT UNIQUE NOT NULL,
        address TEXT NOT NULL,
        area REAL NOT NULL,
        residents INTEGER NOT NULL,
        management_company TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create charges table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS charges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        service TEXT NOT NULL,
        amount REAL NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')

    # Create payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        method TEXT NOT NULL,
        receipt TEXT NOT NULL,
        FOREIGN KEY (account_id) REFERENCES accounts (id)
    )
    ''')

    # Add some test data
    try:
        # Add test user
        cursor.execute('INSERT INTO users (username, password, full_name, email) VALUES (?, ?, ?, ?)',
                      ('test', generate_password_hash('test123'), 'Test User', 'test@example.com'))
        
        # Add test account
        cursor.execute('INSERT INTO accounts (user_id, number, address, area, residents, management_company) VALUES (?, ?, ?, ?, ?, ?)',
                      (1, '12345', 'ул. Примерная, д. 1', 50.0, 2, 'УК Пример'))
        
        # Add test charge
        cursor.execute('INSERT INTO charges (account_id, service, amount, start_date, end_date) VALUES (?, ?, ?, ?, ?)',
                      (1, 'ЖКХ', 5000.0, '2025-10-01', '2025-10-31'))
        
        # Add test payment
        cursor.execute('INSERT INTO payments (account_id, amount, date, method, receipt) VALUES (?, ?, ?, ?, ?)',
                      (1, 5000.0, '2025-10-15', 'Банковская карта', 'REC-001'))
    except sqlite3.IntegrityError:
        pass  # Data already exists

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db() 