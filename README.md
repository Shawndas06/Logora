# Logora - Система учета коммунальных платежей

Простая система для учета и управления коммунальными платежами.

## Возможности

- Управление лицевыми счетами
- Учет начислений за услуги
- Обработка платежей
- Генерация PDF-квитанций
- REST API для интеграции

## Структура проекта

```
.
├── backend/           # C++ бэкенд
│   ├── include/      # Заголовочные файлы
│   └── src/          # Исходный код
├── db/               # База данных
│   ├── schema.sql    # Схема базы данных
│   └── test_data.sql # Тестовые данные
├── python/           # Python приложение
│   ├── app.py        # Основной файл
│   ├── auth.py       # Аутентификация
│   └── pdf_generator.py # Генерация PDF
└── docker-compose.yml # Конфигурация Docker
```

## Установка

1. Установите Docker и Docker Compose
2. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/logora.git
   cd logora
   ```
3. Запустите приложение:
   ```bash
   docker-compose up --build
   ```

## Использование

### API Endpoints

#### Счета
- `GET /api/accounts` - Получить все счета
- `POST /api/accounts` - Создать счет
- `GET /api/accounts/{id}` - Получить счет
- `PUT /api/accounts/{id}` - Обновить счет
- `DELETE /api/accounts/{id}` - Удалить счет

#### Начисления
- `GET /api/charges` - Получить все начисления
- `POST /api/charges` - Создать начисление
- `GET /api/charges/{id}` - Получить начисление
- `PUT /api/charges/{id}` - Обновить начисление
- `DELETE /api/charges/{id}` - Удалить начисление

#### Платежи
- `GET /api/payments` - Получить все платежи
- `POST /api/payments` - Создать платеж
- `GET /api/payments/{id}` - Получить платеж
- `PUT /api/payments/{id}` - Обновить платеж
- `DELETE /api/payments/{id}` - Удалить платеж

### Примеры запросов

#### Создание счета
```bash
curl -X POST http://localhost:8080/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "number": "123456",
    "name": "Иванов Иван",
    "address": "ул. Примерная, 1"
  }'
```

#### Создание начисления
```bash
curl -X POST http://localhost:8080/api/charges \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "service": "Отопление",
    "amount": 1000,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

#### Создание платежа
```bash
curl -X POST http://localhost:8080/api/payments \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "amount": 1000,
    "method": "Карта",
    "receipt": "123456"
  }'
```

## Разработка

### Требования
- C++17
- Python 3.8+
- SQLite 3
- Docker
- Docker Compose

### Сборка
```bash
# Сборка C++ бэкенда
cd backend
mkdir build && cd build
cmake ..
make

# Установка Python зависимостей
cd ../python
pip install -r requirements.txt
```

### Тестирование
```bash
# Запуск тестов
cd backend/build
ctest

cd ../../python
pytest
```

## Лицензия

MIT
