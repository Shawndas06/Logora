#include "account.h"
#include <iostream>
#include <regex>

AccountManager::AccountManager(sqlite3* database) : db(database) {}

bool AccountManager::validateNumber(const std::string& number) const {
    return std::regex_match(number, std::regex("\\d{10}"));
}

void AccountManager::createAccount(int user_id, const std::string& number, const std::string& name,
                                  const std::string& address, double area, int residents, const std::string& company) {
    if (!validateNumber(number)) {
        throw std::invalid_argument("Номер счета должен содержать ровно 10 цифр");
    }
    if (area <= 0 || residents < 0) {
        throw std::invalid_argument("Площадь должна быть положительной, а количество проживающих неотрицательным");
    }
    if (name.empty() || address.empty() || company.empty()) {
        throw std::invalid_argument("ФИО, адрес и управляющая компания не могут быть пустыми");
    }
    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO accounts (user_id, number, name, address, area, residents, company) VALUES (?, ?, ?, ?, ?, ?, ?);";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, user_id);
        sqlite3_bind_text(stmt, 2, number.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 3, name.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 4, address.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_double(stmt, 5, area);
        sqlite3_bind_int(stmt, 6, residents);
        sqlite3_bind_text(stmt, 7, company.c_str(), -1, SQLITE_STATIC);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка создания счета: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
}

std::vector<Account> AccountManager::listAccounts(int user_id) {
    std::vector<Account> accounts;
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, user_id, number, name, address, area, residents, company FROM accounts WHERE user_id = ?;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, user_id);
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Account acc;
            acc.id = sqlite3_column_int(stmt, 0);
            acc.user_id = sqlite3_column_int(stmt, 1);
            acc.number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            acc.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            acc.address = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            acc.area = sqlite3_column_double(stmt, 5);
            acc.residents = sqlite3_column_int(stmt, 6);
            acc.company = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            accounts.push_back(acc);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки счетов: " + std::string(sqlite3_errmsg(db)));
    }
    return accounts;
}

void AccountManager::updateAccount(int id, const std::string& number, const std::string& name,
                                  const std::string& address, double area, int residents, const std::string& company) {
    if (!validateNumber(number)) {
        throw std::invalid_argument("Номер счета должен содержать ровно 10 цифр");
    }
    if (area <= 0 || residents < 0) {
        throw std::invalid_argument("Площадь должна быть положительной, а количество проживающих неотрицательным");
    }
    if (name.empty() || address.empty() || company.empty()) {
        throw std::invalid_argument("ФИО, адрес и управляющая компания не могут быть пустыми");
    }
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE accounts SET number = ?, name = ?, address = ?, area = ?, residents = ?, company = ? WHERE id = ?;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, number.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, name.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 3, address.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_double(stmt, 4, area);
        sqlite3_bind_int(stmt, 5, residents);
        sqlite3_bind_text(stmt, 6, company.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 7, id);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка обновления счета: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
}

void AccountManager::deleteAccount(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "DELETE FROM accounts WHERE id = ?;";
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::string error = "Ошибка удаления счета: " + std::string(sqlite3_errmsg(db));
            sqlite3_finalize(stmt);
            throw std::runtime_error(error);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса: " + std::string(sqlite3_errmsg(db)));
    }
}