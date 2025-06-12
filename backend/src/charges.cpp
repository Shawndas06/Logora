#include "../include/charges.h"
#include <iostream>
#include <iomanip>
#include <sstream>

ChargeManager::ChargeManager(sqlite3* database) : db(database) {
    if (!db) {
        throw std::runtime_error("Database connection is null");
    }
}

ChargeManager::~ChargeManager() {
    // База данных закрывается в main.cpp
}

json ChargeManager::chargeToJson(const Charge& charge) {
    return {
        {"id", charge.id},
        {"account_id", charge.account_id},
        {"service", charge.service},
        {"amount", charge.amount},
        {"start_date", charge.start_date},
        {"end_date", charge.end_date},
        {"status", charge.status}
    };
}

void ChargeManager::create(int account_id, const std::string& service, double amount, 
                         const std::string& start_date, const std::string& end_date) {
    if (amount <= 0) {
        throw std::runtime_error("Сумма должна быть положительной");
    }

    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO charges (account_id, service_name, amount, period_start, period_end, status) "
                     "VALUES (?, ?, ?, ?, ?, 'pending');";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        sqlite3_bind_text(stmt, 2, service.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_double(stmt, 3, amount);
        sqlite3_bind_text(stmt, 4, start_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 5, end_date.c_str(), -1, SQLITE_STATIC);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка создания начисления");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

json ChargeManager::getAll(int account_id) {
    json charges = json::array();
    sqlite3_stmt* stmt;
    const char* sql = account_id > 0 
        ? "SELECT id, account_id, service_name, amount, period_start, period_end, status FROM charges WHERE account_id = ?;"
        : "SELECT id, account_id, service_name, amount, period_start, period_end, status FROM charges;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        if (account_id > 0) {
            sqlite3_bind_int(stmt, 1, account_id);
        }
        
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Charge charge;
            charge.id = sqlite3_column_int(stmt, 0);
            charge.account_id = sqlite3_column_int(stmt, 1);
            charge.service = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            charge.amount = sqlite3_column_double(stmt, 3);
            charge.start_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            charge.end_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            charge.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            
            charges.push_back(chargeToJson(charge));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки начислений");
    }
    
    return charges;
}

json ChargeManager::get(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_id, service_name, amount, period_start, period_end, status "
                     "FROM charges WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            Charge charge;
            charge.id = sqlite3_column_int(stmt, 0);
            charge.account_id = sqlite3_column_int(stmt, 1);
            charge.service = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            charge.amount = sqlite3_column_double(stmt, 3);
            charge.start_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            charge.end_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            charge.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            
            sqlite3_finalize(stmt);
            return chargeToJson(charge);
        }
        sqlite3_finalize(stmt);
    }
    
    throw std::runtime_error("Начисление не найдено");
}

void ChargeManager::update(int id, const std::string& service, double amount, 
                         const std::string& start_date, const std::string& end_date) {
    if (amount <= 0) {
        throw std::runtime_error("Сумма должна быть положительной");
    }

    sqlite3_stmt* stmt;
    const char* sql = "UPDATE charges SET service_name = ?, amount = ?, period_start = ?, period_end = ? "
                     "WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, service.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_double(stmt, 2, amount);
        sqlite3_bind_text(stmt, 3, start_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 4, end_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 5, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка обновления начисления");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void ChargeManager::remove(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "DELETE FROM charges WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка удаления начисления");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void ChargeManager::markPaid(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE charges SET status = 'paid' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка отметки начисления как оплаченного");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void ChargeManager::markPending(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE charges SET status = 'pending' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка отметки начисления как ожидающего оплаты");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

json ChargeManager::getChargesByPeriod(const std::string& start_date, const std::string& end_date) {
    json charges = json::array();
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_id, service_name, amount, period_start, period_end, status, created_at "
                     "FROM charges WHERE period_start >= ? AND period_end <= ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, start_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, end_date.c_str(), -1, SQLITE_STATIC);
        
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Charge charge;
            charge.id = sqlite3_column_int(stmt, 0);
            charge.account_id = sqlite3_column_int(stmt, 1);
            charge.service = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            charge.amount = sqlite3_column_double(stmt, 3);
            charge.start_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            charge.end_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            charge.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            charge.created_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            
            charges.push_back(chargeToJson(charge));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error(std::string("Ошибка выборки начислений: ") + sqlite3_errmsg(db));
    }
    
    return charges;
}

double ChargeManager::getTotalAmount(int account_id) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT SUM(amount) FROM charges WHERE account_id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            double total = sqlite3_column_double(stmt, 0);
            sqlite3_finalize(stmt);
            return total;
        }
        sqlite3_finalize(stmt);
    }
    
    throw std::runtime_error(std::string("Ошибка получения суммы: ") + sqlite3_errmsg(db));
}