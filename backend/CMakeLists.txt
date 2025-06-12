cmake_minimum_required(VERSION 3.10)
project(logora_server VERSION 1.0.0)

# Установка стандарта C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Включение отладочной информации
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -Wall -Wextra")

# Поиск необходимых пакетов
find_package(SQLite3 REQUIRED)
find_package(OpenSSL REQUIRED)

# Проверка версии OpenSSL через pkg-config
execute_process(
    COMMAND pkg-config --modversion openssl
    OUTPUT_VARIABLE OPENSSL_VERSION
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

if(OPENSSL_VERSION VERSION_LESS "3.0.0")
    message(FATAL_ERROR "OpenSSL version must be at least 3.0.0, found ${OPENSSL_VERSION}")
endif()

message(STATUS "Found OpenSSL version: ${OPENSSL_VERSION}")

# Добавление исходных файлов
set(SOURCES
    src/main.cpp
    src/accounts.cpp
    src/charges.cpp
    src/payments.cpp
)

# Добавление заголовочных файлов
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${SQLite3_INCLUDE_DIRS}
    ${OPENSSL_INCLUDE_DIR}
)

# Создание исполняемого файла
add_executable(logora_server ${SOURCES})

# Установка выходной директории
set_target_properties(logora_server PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/bin"
)

# Линковка библиотек
target_link_libraries(logora_server
    ${SQLite3_LIBRARIES}
    ${OPENSSL_LIBRARIES}
    pthread
)

# Установка заголовочных файлов
install(DIRECTORY include/
        DESTINATION include/logora
        FILES_MATCHING PATTERN "*.h")

# Установка исполняемого файла
install(TARGETS logora_server
        RUNTIME DESTINATION bin) 