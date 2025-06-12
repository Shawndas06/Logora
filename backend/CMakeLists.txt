cmake_minimum_required(VERSION 3.10)
project(SmartJKH_Logora)

# Установка стандарта C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Подключение SQLite
find_library(SQLITE3_LIBRARY NAMES sqlite3)
if (NOT SQLITE3_LIBRARY)
    message(FATAL_ERROR "SQLite3 not found")
endif()

# Подключение cpprestsdk
find_package(cpprestsdk REQUIRED)

# Исходные файлы приложения
set(SOURCES
    src/cpp/main.cpp
    src/cpp/account.cpp
    src/cpp/charge.cpp
    src/cpp/payments.cpp
    src/cpp/db.cpp
    src/cpp/api.cpp
)

# Создание исполняемого файла приложения
add_executable(smart_jkh_logora ${SOURCES})
target_link_libraries(smart_jkh_logora PRIVATE ${SQLITE3_LIBRARY} cpprestsdk::cpprest)

# Подключение Catch2 для тестов
find_package(Catch2 REQUIRED)

# Исходные файлы тестов
set(TEST_SOURCES
    tests/cpp/test_account.cpp
    tests/cpp/test_charge.cpp
    tests/cpp/test_payment.cpp
    src/cpp/account.cpp
    src/cpp/charge.cpp
    src/cpp/payments.cpp
    src/cpp/db.cpp
)

# Создание исполняемого файла для тестов
add_executable(tests ${TEST_SOURCES})
target_link_libraries(tests PRIVATE Catch2::Catch2 ${SQLITE3_LIBRARY})

# Включение тестирования
include(CTest)
include(Catch)
catch_discover_tests(tests)