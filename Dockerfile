FROM python:3.11-slim

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/python/receipts /app/python/qrcodes

# Установка прав на выполнение для start.sh
RUN chmod +x /app/start.sh

# Открытие порта
EXPOSE 5000

# Запуск приложения
CMD ["/app/start.sh"]