FROM gcc:latest

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && apt-get install -y \
    cmake \
    libsqlite3-dev \
    libssl-dev \
    curl \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Создание непривилегированного пользователя
RUN useradd -m -s /bin/bash appuser

# Копирование файлов проекта
COPY backend /app/backend
COPY db /app/db

# Создание и настройка прав доступа к директориям
RUN mkdir -p /app/db && \
    chown -R appuser:appuser /app/db && \
    chmod 755 /app/db

WORKDIR /app/backend

# Сборка проекта
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make VERBOSE=1 && \
    chown -R appuser:appuser /app/backend && \
    ls -la bin/ && \
    if [ ! -f bin/logora_server ]; then \
        echo "Error: Binary file not found" && exit 1; \
    fi

# Переключение на непривилегированного пользователя
USER appuser

# Проверка целостности бинарного файла
RUN if [ ! -f build/bin/logora_server ]; then \
        echo "Error: Binary file not found" && exit 1; \
    fi

# Установка переменных окружения
ENV DB_PATH=/app/db/logora.sqlite

# Expose порт
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/health || exit 1

# Запуск сервера
CMD ["./build/bin/logora_server"]
