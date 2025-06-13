CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL,
    isActive BOOLEAN NOT NULL DEFAULT 1,
    address TEXT NOT NULL,
    ownerFullName TEXT NOT NULL,
    propertySquare REAL NOT NULL,
    residentsCount INTEGER NOT NULL,
    companyName TEXT NOT NULL
);

INSERT INTO accounts (id, number, isActive, address, ownerFullName, propertySquare, residentsCount, companyName) VALUES
(1, 'ACC001', 1, 'ул. Ленина, 1', 'Иванов Иван Иванович', 55.5, 3, 'УК Комфорт'),
(2, 'ACC002', 1, 'ул. Ленина, 2', 'Петров Петр Петрович', 60.0, 2, 'УК Уют'),
(3, 'ACC003', 1, 'ул. Ленина, 3', 'Сидоров Сидор Сидорович', 70.0, 4, 'УК Комфорт'),
(4, 'ACC004', 1, 'ул. Ленина, 4', 'Смирнов Смирн Смирнович', 80.0, 5, 'УК Луч'),
(5, 'ACC005', 1, 'ул. Ленина, 5', 'Кузнецов Кузьма Кузьмич', 65.0, 3, 'УК Уют');

INSERT INTO users (id, username, password) VALUES
(1, 'ivanov', 'pass123'),
(2, 'petrov', 'pass123'),
(3, 'sidorov', 'pass123'),
(4, 'smirnov', 'pass123'),
(5, 'kuznetsov', 'pass123');