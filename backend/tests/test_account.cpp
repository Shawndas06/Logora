#include "catch.hpp"
#include "account.h"
#include <sqlite3.h>
#include <stdexcept>

struct DatabaseFixture {
    sqlite3* db;
    DatabaseFixture() {
        sqlite3_open(":memory:", &db);
        const char* sql = R"(
            CREATE TABLE accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                number TEXT,
                name TEXT,
                address TEXT,
                area REAL,
                residents INTEGER,
                company TEXT
            );
        )";
        char* errMsg = nullptr;
        sqlite3_exec(db, sql, nullptr, nullptr, &errMsg);
        if (errMsg) {
            sqlite3_free(errMsg);
        }
    }
    ~DatabaseFixture() {
        sqlite3_close(db);
    }
};

TEST_CASE_METHOD(DatabaseFixture, "AccountManager создание счета", "[account]") {
    AccountManager am(db);

    SECTION("Создание валидного счета") {
        REQUIRE_NOTHROW(am.createAccount(1, "1234567890", "Иван Иванов", "ул. Главная, 123", 50.5, 2, "КомпанияА"));
        auto accounts = am.listAccounts(1);
        REQUIRE(accounts.size() == 1);
        REQUIRE(accounts[0].user_id == 1);
        REQUIRE(accounts[0].number == "1234567890");
        REQUIRE(accounts[0].name == "Иван Иванов");
        REQUIRE(accounts[0].address == "ул. Главная, 123");
        REQUIRE(accounts[0].area == Approx(50.5));
        REQUIRE(accounts[0].residents == 2);
        REQUIRE(accounts[0].company == "КомпанияА");
    }

    SECTION("Недопустимый номер счета") {
        REQUIRE_THROWS_AS(am.createAccount(1, "123", "Иван Иванов", "ул. Главная, 123", 50.5, 2, "КомпанияА"),
                         std::invalid_argument);
    }

    SECTION("Отрицательная площадь") {
        REQUIRE_THROWS_AS(am.createAccount(1, "1234567890", "Иван Иванов", "ул. Главная, 123", -50.5, 2, "КомпанияА"),
                         std::invalid_argument);
    }

    SECTION("Пустое имя") {
        REQUIRE_THROWS_AS(am.createAccount(1, "1234567890", "", "ул. Главная, 123", 50.5, 2, "КомпанияА"),
                         std::invalid_argument);
    }
}

TEST_CASE_METHOD(DatabaseFixture, "AccountManager обновление счета", "[account]") {
    AccountManager am(db);
    am.createAccount(1, "1234567890", "Иван Иванов", "ул. Главная, 123", 50.5, 2, "КомпанияА");

    SECTION("Валидное обновление") {
        auto accounts = am.listAccounts(1);
        int id = accounts[0].id;
        REQUIRE_NOTHROW(am.updateAccount(id, "0987654321", "Анна Иванова", "ул. Новая, 456", 60.0, 3, "КомпанияБ"));
        accounts = am.listAccounts(1);
        REQUIRE(accounts[0].number == "0987654321");
        REQUIRE(accounts[0].name == "Анна Иванова");
        REQUIRE(accounts[0].address == "ул. Новая, 456");
        REQUIRE(accounts[0].area == Approx(60.0));
        REQUIRE(accounts[0].residents == 3);
        REQUIRE(accounts[0].company == "КомпанияБ");
    }

    SECTION("Недопустимый номер при обновлении") {
        auto accounts = am.listAccounts(1);
        int id = accounts[0].id;
        REQUIRE_THROWS_AS(am.updateAccount(id, "123", "Анна Иванова", "ул. Новая, 456", 60.0, 3, "КомпанияБ"),
                         std::invalid_argument);
    }
}

TEST_CASE_METHOD(DatabaseFixture, "AccountManager удаление счета", "[account]") {
    AccountManager am(db);
    am.createAccount(1, "1234567890", "Иван Иванов", "ул. Главная, 123", 50.5, 2, "КомпанияА");
    auto accounts = am.listAccounts(1);
    int id = accounts[0].id;

    SECTION("Валидное удаление") {
        REQUIRE_NOTHROW(am.deleteAccount(id));
        accounts = am.listAccounts(1);
        REQUIRE(accounts.empty());
    }
}

TEST_CASE_METHOD(DatabaseFixture, "AccountManager список счетов", "[account]") {
    AccountManager am(db);
    am.createAccount(1, "1234567890", "Иван Иванов", "ул. Главная, 123", 50.5, 2, "КомпанияА");
    am.createAccount(1, "0987654321", "Анна Иванова", "ул. Новая, 456", 60.0, 3, "КомпанияБ");

    SECTION("Список счетов для пользователя") {
        auto accounts = am.listAccounts(1);
        REQUIRE(accounts.size() == 2);
        REQUIRE(accounts[0].user_id == 1);
        REQUIRE(accounts[1].user_id == 1);
    }

    SECTION("Список счетов для несуществующего пользователя") {
        auto accounts = am.listAccounts(2);
        REQUIRE(accounts.empty());
    }
}