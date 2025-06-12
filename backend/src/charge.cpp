#include "charge.h"
#include <iostream>
#include <iomanip>

ChargeManager::ChargeManager(sqlite3* database) : db(database) {}

void ChargeManager::addCharge(int account_id, const std::string& service_type, double tariff, double volume, const std::string& period) {
    if (tariff < 0 || volume < 0) {
        throw std::invalid_argument("Тариф и объем не могут быть отрицательными");
    }
    if (service_type.empty() || period.empty()) {
        throw std::invalid_argument("Тип услуги и период не могут быть пустыми");
    }
    double amount = tariff * volume;
    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO charges (account_id, service_type, tariff, volume, amount, period, status) VALUES (?, ?, ?, ?, ?, ?, 'unpaid');";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        sqlite3_bind_text(stmt, 2, service_type.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_double(stmt, 3, tariff);
        sqlite3_bind_double(stmt, 4, volume);
        sqlite3_bind_double(stmt, 5, amount);
        sqlite3_bind_text(stmt, 6, period.c_str(), -1, SQLITE_STATIC);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка добавления начисления: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
}

std::vector<Charge> ChargeManager::listCharges(int account_id, const std::string& period) {
    std::vector<Charge> charges;
    sqlite3_stmt* stmt;
    std::string sql = "SELECT id, account_id, service_type, tariff, volume, amount, period, status FROM charges WHERE account_id = ?";
    if (!period.empty()) {
        sql += " AND period = ?";
    }
    sql += ";";
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        if (!period.empty()) {
            sqlite3_bind_text(stmt, 2, period.c_str(), -1, SQLITE_STATIC);
        }
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Charge charge;
            charge.id = sqlite3_column_int(stmt, 0);
            charge.account_id = sqlite3_column_int(stmt, 1);
            charge.service_type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            charge.tariff = sqlite3_column_double(stmt, 3);
            charge.volume = sqlite3_column_double(stmt, 4);
            charge.amount = sqlite3_column_double(stmt, 5);
            charge.period = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            charge.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            charges.push_back(charge);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки начислений: " + std::string(sqlite3_errmsg(db)));
    }
    return charges;
}