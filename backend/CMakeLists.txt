cmake_minimum_required(VERSION 3.10)
project(logora_server VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Настройка путей вывода
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Поиск зависимостей
find_package(OpenSSL REQUIRED)
find_package(SQLite3 REQUIRED)
find_package(cpprestsdk REQUIRED)
find_package(Threads REQUIRED)

# Исходные файлы
set(SOURCES
    src/main.cpp
    src/account.cpp
    src/charge.cpp
    src/payments.cpp
    src/db.cpp
    src/api.cpp
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
    Threads::Threads
)

# Тесты (опционально)
option(BUILD_TESTS "Build tests" OFF)

if(BUILD_TESTS)
    find_package(Catch2 REQUIRED)
    
    set(TEST_SOURCES
        tests/test_account.cpp
        tests/test_charge.cpp
        tests/test_payment.cpp
    )
    
    add_executable(tests ${TEST_SOURCES})
    target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
    
    include(CTest)
    include(Catch)
    catch_discover_tests(tests)
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