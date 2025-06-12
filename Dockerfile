# Используем более новый Python-образ с OpenSSL 3.0+
FROM python:3.11-slim AS base

# Установим системные зависимости с добавлением libssl-dev
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libssl-dev \  # КРИТИЧНОЕ ИСПРАВЛЕНИЕ
    curl \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем проект
COPY backend /app/backend
COPY python /app/python
COPY db /app/db

# Установка зависимостей Python
WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

# Сборка C++ сервера (остаётся без изменений)
WORKDIR /app/backend
RUN mkdir -p build && cd build && cmake .. && make && \
    ls -la bin/ && \
    if [ ! -f bin/logora_server ]; then \
        echo "Error: C++ binary not found" && exit 1; \
    fi

# Подготовка директорий
WORKDIR /app
RUN mkdir -p /app/db \
    /app/python/receipts \
    /app/python/qrcodes \
    /app/python/logs && \
    chmod -R 777 /app/db /app/python/receipts /app/python/qrcodes /app/python/logs

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///db/logora.sqlite
ENV DB_PATH=/app/db/logora.sqlite
ENV LOG_FILE=/app/python/logs/app.log
ENV LOG_LEVEL=INFO

# Проброс портов
EXPOSE 8000
EXPOSE 8080

# Добавляем start.sh
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🔧 Инициализация БД..."\n\
python /app/python/init_db.py\n\
echo "🚀 Запуск C++ сервера..."\n\
/app/backend/build/bin/logora_server &\n\
echo "🌐 Запуск FastAPI..."\n\
python -m uvicorn python.app:app --host 0.0.0.0 --port 8000\n' > /app/start.sh && chmod +x /app/start.sh

# Запуск скрипта
CMD ["/app/start.sh"]
