#include "catch.hpp"
#include "charge.h"
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

TEST_CASE_METHOD(DatabaseFixture, "ChargeManager добавление начисления", "[charge]") {
    ChargeManager cm(db);

    SECTION("Валидное добавление начисления") {
        REQUIRE_NOTHROW(cm.addCharge(1, "Вода", 10.0, 5.0, "2023-01"));
        auto charges = cm.listCharges(1, "");
        REQUIRE(charges.size() == 1);
        REQUIRE(charges[0].account_id == 1);
        REQUIRE(charges[0].service_type == "Вода");
        REQUIRE(charges[0].tariff == Approx(10.0));
        REQUIRE(charges[0].volume == Approx(5.0));
        REQUIRE(charges[0].amount == Approx(50.0));
        REQUIRE(charges[0].period == "2023-01");
        REQUIRE(charges[0].status == "unpaid");
    }

    SECTION("Отрицательный тариф") {
        REQUIRE_THROWS_AS(cm.addCharge(1, "Вода", -10.0, 5.0, "2023-01"),
                         std::invalid_argument);
    }

    SECTION("Пустой тип услуги") {
        REQUIRE_THROWS_AS(cm.addCharge(1, "", 10.0, 5.0, "2023-01"),
                         std::invalid_argument);
    }

    SECTION("Пустой период") {
        REQUIRE_THROWS_AS(cm.addCharge(1, "Вода", 10.0, 5.0, ""),
                         std::invalid_argument);
    }
}

TEST_CASE_METHOD(DatabaseFixture, "ChargeManager список начислений", "[charge]") {
    ChargeManager cm(db);
    cm.addCharge(1, "Вода", 10.0, 5.0, "2023-01");
    cm.addCharge(1, "Электричество", 20.0, 3.0, "2023-01");
    cm.addCharge(1, "Газ", 15.0, 2.0, "2023-02");

    SECTION("Список всех начислений для счета") {
        auto charges = cm.listCharges(1, "");
        REQUIRE(charges.size() == 3);
        REQUIRE(charges[0].account_id == 1);
        REQUIRE(charges[1].account_id == 1);
        REQUIRE(charges[2].account_id == 1);
    }

    SECTION("Список начислений за определенный период") {
        auto charges = cm.listCharges(1, "2023-01");
        REQUIRE(charges.size() == 2);
        REQUIRE(charges[0].period == "2023-01");
        REQUIRE(charges[1].period == "2023-01");
    }

    SECTION("Список начислений для несуществующего счета") {
        auto charges = cm.listCharges(2, "");
        REQUIRE(charges.empty());
    }
}