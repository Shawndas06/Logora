FROM python:3.11-slim AS base

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libssl-dev \
    libcpprest-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    pkg-config \
    git \
    tree \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Проверка структуры проекта перед копированием
RUN echo "----- Структура проекта до копирования -----" && \
    ls -la && \
    mkdir -p backend && \
    tree -L 3 || echo "Tree не установлен"

# Копирование файлов проекта с проверкой
COPY backend/CMakeLists.txt /app/backend/
COPY backend/src /app/backend/src
COPY backend/include /app/backend/include

# Проверка скопированных файлов
RUN echo "----- Проверка файлов проекта -----" && \
    echo "1. Содержимое /app/backend:" && ls -la /app/backend/ && \
    echo "2. Содержимое src:" && ls -la /app/backend/src/ && \
    echo "3. Содержимое include:" && ls -la /app/backend/include/ && \
    echo "4. Проверка CMakeLists.txt:" && [ -f /app/backend/CMakeLists.txt ] && cat /app/backend/CMakeLists.txt || echo "CMakeLists.txt не найден"

# Сборка с подробной отладкой
WORKDIR /app/backend
RUN mkdir -p build && cd build && \
    echo "----- Конфигурация CMake -----" && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    echo "----- Сборка проекта -----" && \
    make VERBOSE=1

# Проверка результатов сборки
RUN echo "----- Результаты сборки -----" && \
    if [ -f build/bin/logora_server ]; then \
        echo "Бинарник успешно создан:" && \
        ls -la build/bin/logora_server && \
        echo "Проверка зависимостей:" && \
        ldd build/bin/logora_server || true; \
    else \
        echo "----- ОШИБКА: Бинарник не создан -----" && \
        echo "1. Поиск возможных бинарников:" && find build -type f -executable -print || true; \
        echo "2. Содержимое build:" && ls -la build/; \
        echo "3. Логи CMake:" && (find build -name "*.log" -exec cat {} \; || true); \
        exit 1; \
    fi

# Установка Python зависимостей
COPY python /app/python
COPY db /app/db

WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
CMD ["python", "-m", "uvicorn", "python.app:app", "--host", "0.0.0.0", "--port", "8000"]