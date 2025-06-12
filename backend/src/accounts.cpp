#include "../include/accounts.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <ctime>

AccountManager::AccountManager(sqlite3* database) : db(database) {
    if (!db) {
        throw std::runtime_error("Database connection is null");
    }
}

AccountManager::~AccountManager() {
    // База данных закрывается в main.cpp
}

json AccountManager::accountToJson(const Account& account) {
    return {
        {"id", account.id},
        {"number", account.number},
        {"name", account.name},
        {"address", account.address},
        {"status", account.status}
    };
}

void AccountManager::create(const std::string& number, const std::string& name, const std::string& address) {
    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO accounts (account_number, full_name, address, status) VALUES (?, ?, ?, 'active');";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, number.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, name.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 3, address.c_str(), -1, SQLITE_STATIC);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка создания счета");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

json AccountManager::getAll() {
    json accounts = json::array();
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_number, full_name, address, status FROM accounts;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Account account;
            account.id = sqlite3_column_int(stmt, 0);
            account.number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            account.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            account.address = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            account.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            
            accounts.push_back(accountToJson(account));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки счетов");
    }
    
    return accounts;
}

json AccountManager::get(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_number, full_name, address, status FROM accounts WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            Account account;
            account.id = sqlite3_column_int(stmt, 0);
            account.number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            account.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            account.address = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            account.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            
            sqlite3_finalize(stmt);
            return accountToJson(account);
        }
        sqlite3_finalize(stmt);
    }
    
    throw std::runtime_error("Счет не найден");
}

void AccountManager::update(int id, const std::string& number, const std::string& name, const std::string& address) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE accounts SET account_number = ?, full_name = ?, address = ? WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, number.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, name.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 3, address.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 4, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка обновления счета");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void AccountManager::remove(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "DELETE FROM accounts WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка удаления счета");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void AccountManager::activate(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE accounts SET status = 'active' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка активации счета");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

void AccountManager::deactivate(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE accounts SET status = 'inactive' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка деактивации счета");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

json AccountManager::getAccountsByUser(int userId) {
    json accounts = json::array();
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_number, full_name, address, status, created_at, updated_at FROM accounts WHERE user_id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, userId);
        
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Account account;
            account.id = sqlite3_column_int(stmt, 0);
            account.number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            account.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            account.address = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            account.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            account.created_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            account.updated_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            
            accounts.push_back(accountToJson(account));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error(std::string("Ошибка выборки счетов: ") + sqlite3_errmsg(db));
    }
    
    return accounts;
}

bool AccountManager::accountExists(const std::string& account_number) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT COUNT(*) FROM accounts WHERE account_number = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, account_number.c_str(), -1, SQLITE_STATIC);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            int count = sqlite3_column_int(stmt, 0);
            sqlite3_finalize(stmt);
            return count > 0;
        }
        sqlite3_finalize(stmt);
    }
    
    return false;
}