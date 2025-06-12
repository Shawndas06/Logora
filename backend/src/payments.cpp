#include "../include/payments.h"
#include <iostream>
#include <ctime>

PaymentManager::PaymentManager(sqlite3* database) : db(database) {}

void PaymentManager::makePayment(int charge_id, double amount) {
    if (amount <= 0) {
        throw std::invalid_argument("Сумма оплаты должна быть положительной");
    }
    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO payments (charge_id, amount, payment_date) VALUES (?, ?, ?);";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, charge_id);
        sqlite3_bind_double(stmt, 2, amount);
        time_t now = time(nullptr);
        std::string date = ctime(&now);
        date.pop_back();
        sqlite3_bind_text(stmt, 3, date.c_str(), -1, SQLITE_STATIC);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка добавления оплаты: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
    const char* update_sql = "UPDATE charges SET status = 'paid' WHERE id = ?;";
    if (sqlite3_prepare_v2(db, update_sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, charge_id);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка обновления статуса начисления: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
}

void PaymentManager::payAllCharges(int account_id, const std::string& period) {
    sqlite3_stmt* stmt;
    std::string sql = "SELECT id, amount FROM charges WHERE account_id = ? AND status = 'unpaid'";
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
            int charge_id = sqlite3_column_int(stmt, 0);
            double amount = sqlite3_column_double(stmt, 1);
            makePayment(charge_id, amount);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки начислений для оплаты: " + std::string(sqlite3_errmsg(db)));
    }
}

std::vector<Payment> PaymentManager::listPayments(int account_id) {
    std::vector<Payment> payments;
    sqlite3_stmt* stmt;
     std::string sql = "SELECT p.id, p.charge_id, p.amount, p.payment_date "
                      "FROM payments p JOIN charges c ON p.charge_id = c.id "
                      "WHERE c.account_id = ?;";
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Payment payment;
            payment.id = sqlite3_column_int(stmt, 0);
            payment.charge_id = sqlite3_column_int(stmt, 1);
            payment.amount = sqlite3_column_double(stmt, 2);
            payment.payment_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            payments.push_back(payment);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки платежей: " + std::string(sqlite3_errmsg(db)));
    }
    return payments;
}