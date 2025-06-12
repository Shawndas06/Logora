# Используем более новый Python-образ с OpenSSL 3.0+
FROM python:3.11-slim AS base

# Установим системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libssl-dev \
    libcpprest-dev \
    libboost-system-dev \
    libboost-date-time-dev \
    libboost-filesystem-dev \
    curl \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Остальная часть Dockerfile остается без изменений
COPY backend /app/backend
COPY python /app/python
COPY db /app/db
COPY python/static /app/python/static
COPY python/templates /app/python/templates

WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/backend
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make && \
    ls -la bin/ && \
    if [ ! -f bin/smart_jkh_logora ]; then \
        echo "Error: C++ binary not found" && exit 1; \
    fi

WORKDIR /app
RUN mkdir -p /app/db \
    /app/python/receipts \
    /app/python/qrcodes \
    /app/python/logs && \
    chmod -R 777 /app/db /app/python/receipts /app/python/qrcodes /app/python/logs

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///db/logora.sqlite
ENV DB_PATH=/app/db/logora.sqlite
ENV LOG_FILE=/app/python/logs/app.log
ENV LOG_LEVEL=INFO
ENV STATIC_URL=/static
ENV STATIC_PATH=/app/python/static
ENV TEMPLATES_PATH=/app/python/templates

EXPOSE 8000
EXPOSE 8080

RUN echo '#!/bin/bash\n\
set -e\n\
echo "🔧 Инициализация БД..."\n\
python /app/python/init_db.py\n\
echo "🚀 Запуск C++ сервера..."\n\
/app/backend/build/bin/smart_jkh_logora &\n\
echo "🌐 Запуск FastAPI с поддержкой статических файлов..."\n\
python -m uvicorn python.app:app --host 0.0.0.0 --port 8000\n' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]