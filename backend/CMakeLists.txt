cmake_minimum_required(VERSION 3.12)
project(logora_server LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Настройка путей вывода
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Поиск обязательных зависимостей
find_package(OpenSSL 1.1.1 REQUIRED)
find_package(SQLite3 REQUIRED)
find_package(cpprestsdk 2.10 REQUIRED)
find_package(Boost REQUIRED COMPONENTS system filesystem)

# Проверка версий
message(STATUS "OpenSSL version: ${OPENSSL_VERSION}")
message(STATUS "Boost version: ${Boost_VERSION}")

# Исходные файлы
set(SOURCES
    src/cpp/main.cpp
    src/cpp/account.cpp
    src/cpp/charge.cpp
    src/cpp/payments.cpp
    src/cpp/db.cpp
    src/cpp/api.cpp
)

# Основной сервер
add_executable(logora_server ${SOURCES})

target_include_directories(logora_server PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(logora_server PRIVATE
    SQLite::SQLite3
    cpprestsdk::cpprest
    OpenSSL::SSL
    OpenSSL::Crypto
    Boost::system
    Boost::filesystem
    pthread
)

# Установка бинарника
install(TARGETS logora_server DESTINATION bin)