FROM python:3.11-slim AS base

# Установка зависимостей с доступными версиями пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libsqlite3-dev \
    libssl-dev \
    libcpprest2.10 \
    libboost-system-dev \
    libboost-filesystem-dev \
    g++-10 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Настройка альтернативных версий компилятора
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 100

WORKDIR /app

# Копирование только необходимых файлов
COPY backend/CMakeLists.txt /app/backend/
COPY backend/src /app/backend/src
COPY backend/include /app/backend/include

# Сборка C++ сервера
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

# Остальные шаги...
COPY python /app/python
COPY db /app/db

WORKDIR /app/python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
CMD ["python", "-m", "uvicorn", "python.app:app", "--host", "0.0.0.0", "--port", "8000"]