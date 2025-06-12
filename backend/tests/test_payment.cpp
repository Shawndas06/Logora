#include "catch.hpp"
#include "payments.h"
#include <sqlite3.h>
#include <stdexcept>

struct DatabaseFixture {
    sqlite3* db;
    DatabaseFixture() {
        sqlite3_open(":memory:", &db);
        const char* sql = R"(
            CREATE TABLE charges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                service_type TEXT,
                tariff REAL,
                volume REAL,
                amount REAL,
                period TEXT,
                status TEXT
            );
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charge_id INTEGER,
                amount REAL,
                payment_date TEXT
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

    void addCharge(int account_id, double amount, const std::string& period) {
        sqlite3_stmt* stmt;
        const char* sql = "INSERT INTO charges (account_id, amount, period, status) VALUES (?, ?, ?, 'unpaid');";
        if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
            sqlite3_bind_int(stmt, 1, account_id);
            sqlite3_bind_double(stmt, 2, amount);
            sqlite3_bind_text(stmt, 3, period.c_str(), -1, SQLITE_STATIC);
            sqlite3_step(stmt);
            sqlite3_finalize(stmt);
        }
    }
};

TEST_CASE_METHOD(DatabaseFixture, "PaymentManager создание платежа", "[payment]") {
    PaymentManager pm(db);
    addCharge(1, 100.0, "2023-01");

    SECTION("Валидный платеж") {
        REQUIRE_NOTHROW(pm.makePayment(1, 100.0));
        auto payments = pm.listPayments(1);
        REQUIRE(payments.size() == 1);
        REQUIRE(payments[0].charge_id == 1);
        REQUIRE(payments[0].amount == Approx(100.0));

        sqlite3_stmt* stmt;
        const char* sql = "SELECT status FROM charges WHERE id = 1;";
        REQUIRE(sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK);
        sqlite3_step(stmt);
        REQUIRE(std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0))) == "paid");
        sqlite3_finalize(stmt);
    }

    SECTION("Отрицательная сумма") {
        REQUIRE_THROWS_AS(pm.makePayment(1, -100.0), std::invalid_argument);
    }
}

TEST_CASE_METHOD(DatabaseFixture, "PaymentManager оплата всех начислений", "[payment]") {
    PaymentManager pm(db);
    addCharge(1, 100.0, "2023-01");
    addCharge(1, 200.0, "2023-01");
    addCharge(1, 300.0, "2023-02");

    SECTION("Оплата всех начислений для счета") {
        REQUIRE_NOTHROW(pm.payAllCharges(1, ""));
        auto payments = pm.listPayments(1);
        REQUIRE(payments.size() == 3);
        REQUIRE(payments[0].amount == Approx(100.0) || payments[0].amount == Approx(200.0) || payments[0].amount == Approx(300.0));
    }

    SECTION("Оплата начислений за определенный период") {
        REQUIRE_NOTHROW(pm.payAllCharges(1, "2023-01"));
        auto payments = pm.listPayments(1);
        REQUIRE(payments.size() == 2);
        REQUIRE(payments[0].amount == Approx(100.0) || payments[0].amount == Approx(200.0));
    }
}

TEST_CASE_METHOD(DatabaseFixture, "PaymentManager список платежей", "[payment]") {
    PaymentManager pm(db);
    addCharge(1, 100.0, "2023-01");
    addCharge(1, 200.0, "2023-01");
    pm.makePayment(1, 100.0);
    pm.makePayment(2, 200.0);

    SECTION("Список платежей для счета") {
        auto payments = pm.listPayments(1);
        REQUIRE(payments.size() == 2);
        REQUIRE(payments[0].charge_id == 1 || payments[0].charge_id == 2);
        REQUIRE(payments[1].charge_id == 1 || payments[1].charge_id == 2);
    }

    SECTION("Список платежей для несуществующего счета") {
        auto payments = pm.listPayments(2);
        REQUIRE(payments.empty());
    }
}