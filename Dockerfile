# Базовый образ
FROM python:3.11-slim AS base

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libssl-dev \
    libcpprest-dev \
    libboost-system-dev \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование файлов
COPY backend /app/backend
COPY python /app/python
COPY db /app/db
COPY python/static /app/python/static
COPY python/templates /app/python/templates

# Установка Python зависимостей
WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

# Сборка C++ сервера
WORKDIR /app/backend
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make && \
    ls -la bin/ && \
    if [ ! -f bin/logora_server ]; then \
        echo "Error: C++ binary not found" && exit 1; \
    fi

# Настройка окружения
WORKDIR /app
RUN mkdir -p /app/db \
    /app/python/receipts \
    /app/python/qrcodes \
    /app/python/logs && \
    chmod -R 777 /app/db /app/python/receipts /app/python/qrcodes /app/python/logs

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///db/logora.sqlite
ENV DB_PATH=/app/db/logora.sqlite

# Скрипт запуска
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🔧 Инициализация БД..."\n\
python /app/python/init_db.py\n\
echo "🚀 Запуск C++ сервера..."\n\
/app/backend/build/bin/logora_server &\n\
echo "🌐 Запуск FastAPI..."\n\
python -m uvicorn python.app:app --host 0.0.0.0 --port 8000\n' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE 8000
CMD ["/app/start.sh"]