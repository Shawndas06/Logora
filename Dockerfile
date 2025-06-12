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

RUN echo "----- Проверка скопированных файлов -----" && \
    ls -la /app/backend/ && \
    ls -la /app/backend/src/ && \
    ls -la /app/backend/include/ && \
    cat /app/backend/CMakeLists.txt || echo "CMakeLists.txt не найден"

# Сборка с подробной отладкой (см. выше)
WORKDIR /app/backend
RUN mkdir -p build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make VERBOSE=1 && \
    ls -la bin/

# Проверка существования бинарника
RUN if [ ! -f build/bin/logora_server ]; then \
        echo "----- Содержимое build/ -----" && \
        ls -la build/ && \
        echo "----- Содержимое build/bin/ -----" && \
        ls -la build/bin/ && \
        echo "----- Лог CMake -----" && \
        cat build/CMakeFiles/CMakeOutput.log && \
        exit 1; \
    fi

# Установка Python зависимостей
COPY python /app/python
COPY db /app/db

WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
CMD ["python", "-m", "uvicorn", "python.app:app", "--host", "0.0.0.0", "--port", "8000"]