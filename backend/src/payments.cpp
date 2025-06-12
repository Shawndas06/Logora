#include "../include/payments.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <random>
#include <chrono>

// Создание менеджера платежей
PaymentManager::PaymentManager(sqlite3* database) : db(database) {
    if (!db) {
        throw std::runtime_error("Database connection is null");
    }
}

// Удаление менеджера платежей
PaymentManager::~PaymentManager() {}

// Генерация номера квитанции
std::string PaymentManager::generateReceiptNumber() {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_time_t), "%Y%m%d%H%M%S");
    ss << std::setfill('0') << std::setw(3) << now_ms.count();
    
    return ss.str();
}

// Преобразование платежа в JSON
json PaymentManager::paymentToJson(const Payment& payment) {
    return {
        {"id", payment.id},
        {"account_id", payment.account_id},
        {"amount", payment.amount},
        {"payment_date", payment.payment_date},
        {"receipt_number", payment.receipt_number},
        {"status", payment.status},
        {"created_at", payment.created_at},
        {"updated_at", payment.updated_at}
    };
}

// Создание нового платежа
void PaymentManager::create(int account_id, double amount, const std::string& payment_date) {
    if (amount <= 0) {
        throw std::runtime_error("Сумма должна быть положительной");
    }

    std::string receipt_number = generateReceiptNumber();
    sqlite3_stmt* stmt;
    const char* sql = "INSERT INTO payments (account_id, amount, payment_date, receipt_number, status) "
                     "VALUES (?, ?, ?, ?, 'pending');";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        sqlite3_bind_double(stmt, 2, amount);
        sqlite3_bind_text(stmt, 3, payment_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 4, receipt_number.c_str(), -1, SQLITE_STATIC);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка создания платежа");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

// Получение всех платежей
json PaymentManager::getAll(int account_id) {
    json payments = json::array();
    sqlite3_stmt* stmt;
    const char* sql = account_id > 0 
        ? "SELECT id, account_id, amount, payment_date, receipt_number, status, created_at, updated_at FROM payments WHERE account_id = ?;"
        : "SELECT id, account_id, amount, payment_date, receipt_number, status, created_at, updated_at FROM payments;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        if (account_id > 0) {
            sqlite3_bind_int(stmt, 1, account_id);
        }
        
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Payment payment;
            payment.id = sqlite3_column_int(stmt, 0);
            payment.account_id = sqlite3_column_int(stmt, 1);
            payment.amount = sqlite3_column_double(stmt, 2);
            payment.payment_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            payment.receipt_number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            payment.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            payment.created_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            payment.updated_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            
            payments.push_back(paymentToJson(payment));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки платежей");
    }
    
    return payments;
}

// Получение платежа по ID
json PaymentManager::get(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_id, amount, payment_date, receipt_number, status, created_at, updated_at "
                     "FROM payments WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            Payment payment;
            payment.id = sqlite3_column_int(stmt, 0);
            payment.account_id = sqlite3_column_int(stmt, 1);
            payment.amount = sqlite3_column_double(stmt, 2);
            payment.payment_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            payment.receipt_number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            payment.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            payment.created_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            payment.updated_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            
            sqlite3_finalize(stmt);
            return paymentToJson(payment);
        }
        sqlite3_finalize(stmt);
    }
    
    throw std::runtime_error("Платеж не найден");
}

// Обновление платежа
void PaymentManager::update(int id, double amount, const std::string& payment_date) {
    if (amount <= 0) {
        throw std::runtime_error("Сумма должна быть положительной");
    }

    sqlite3_stmt* stmt;
    const char* sql = "UPDATE payments SET amount = ?, payment_date = ? WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_double(stmt, 1, amount);
        sqlite3_bind_text(stmt, 2, payment_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_int(stmt, 3, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка обновления платежа");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

// Удаление платежа
void PaymentManager::remove(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "DELETE FROM payments WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка удаления платежа");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

// Отметка платежа как выполненного
void PaymentManager::markCompleted(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE payments SET status = 'completed' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка отметки платежа как выполненного");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

// Отметка платежа как ожидающего
void PaymentManager::markPending(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "UPDATE payments SET status = 'pending' WHERE id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("Ошибка отметки платежа как ожидающего");
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подготовки запроса");
    }
}

json PaymentManager::getPaymentsByPeriod(const std::string& start_date, const std::string& end_date) {
    json payments = json::array();
    sqlite3_stmt* stmt;
    const char* sql = "SELECT id, account_id, amount, payment_date, receipt_number, status, created_at, updated_at "
                     "FROM payments WHERE payment_date >= ? AND payment_date <= ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, start_date.c_str(), -1, SQLITE_STATIC);
        sqlite3_bind_text(stmt, 2, end_date.c_str(), -1, SQLITE_STATIC);
        
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Payment payment;
            payment.id = sqlite3_column_int(stmt, 0);
            payment.account_id = sqlite3_column_int(stmt, 1);
            payment.amount = sqlite3_column_double(stmt, 2);
            payment.payment_date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            payment.receipt_number = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            payment.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5));
            payment.created_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6));
            payment.updated_at = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7));
            
            payments.push_back(paymentToJson(payment));
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка выборки платежей за период");
    }
    
    return payments;
}

double PaymentManager::getTotalPayments(int account_id) {
    double total = 0.0;
    sqlite3_stmt* stmt;
    const char* sql = "SELECT SUM(amount) FROM payments WHERE account_id = ? AND status = 'completed';";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, account_id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            total = sqlite3_column_double(stmt, 0);
        }
        sqlite3_finalize(stmt);
    } else {
        throw std::runtime_error("Ошибка подсчета общей суммы платежей");
    }
    
    return total;
}

json PaymentManager::getPaymentReceipt(int id) {
    sqlite3_stmt* stmt;
    const char* sql = "SELECT p.id, p.account_id, p.amount, p.payment_date, p.receipt_number, p.status, "
                     "a.account_number, a.name, a.address "
                     "FROM payments p "
                     "JOIN accounts a ON p.account_id = a.id "
                     "WHERE p.id = ?;";
    
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            json receipt = {
                {"id", sqlite3_column_int(stmt, 0)},
                {"account_id", sqlite3_column_int(stmt, 1)},
                {"amount", sqlite3_column_double(stmt, 2)},
                {"payment_date", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3))},
                {"receipt_number", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4))},
                {"status", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 5))},
                {"account_number", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 6))},
                {"account_name", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 7))},
                {"account_address", reinterpret_cast<const char*>(sqlite3_column_text(stmt, 8))}
            };
            
            sqlite3_finalize(stmt);
            return receipt;
        }
        sqlite3_finalize(stmt);
    }
    
    throw std::runtime_error("Квитанция не найдена");
}