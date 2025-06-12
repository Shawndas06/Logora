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

# Проверка результатов сборки с подробной диагностикой
RUN echo "----- Анализ результатов сборки -----" && \
    if [ -f build/bin/logora_server ]; then \
        echo "Бинарник успешно создан:" && \
        ls -la build/bin/logora_server && \
        echo "Проверка зависимостей:" && \
        ldd build/bin/logora_server || true; \
    else \
        echo "----- ВНИМАНИЕ: Бинарник не создан -----" && \
        echo "----- Содержимое build/ -----" && \
        ls -la build/ && \
        echo "----- Поиск возможных бинарников -----" && \
        find build -type f -executable -print || echo "Исполняемые файлы не найдены"; \
        echo "----- Логи CMake -----" && \
        (cat build/CMakeCache.txt 2>/dev/null || echo "CMakeCache.txt не найден") && \
        (cat build/CMakeFiles/*.log 2>/dev/null || echo "Логи CMake не найдены"); \
        echo "----- Проверка исходных файлов -----" && \
        ls -la /app/backend/src/ && \
        echo "----- Проверка заголовочных файлов -----" && \
        ls -la /app/backend/include/; \
        # Не завершаем с ошибкой, чтобы увидеть всю диагностику \
        # exit 1; \
    fi

# Установка Python зависимостей
COPY python /app/python
COPY db /app/db

WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
CMD ["python", "-m", "uvicorn", "python.app:app", "--host", "0.0.0.0", "--port", "8000"]