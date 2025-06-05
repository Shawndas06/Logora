#include <iostream>
#include <sqlite3.h>
#include <string>

class Payment {
    public:
    static bool createPayment (sqlite3* db, int chargeId, double amount, const std::string& date){
        const char* sql = "INSERT INTO payments (charge_id, amount, date) VALUES (?, ?, ?)";
        sqlite3_stmt* stmt;

    int rc =  sqlite3_prepare(db, sql, -1, &stmt, nullptr);
    if (rc != SQLITE_OK) {
        std::cerr << "Ошибка подготовки запроса: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    sqlite3_bind_int(stmt, 1, chargeId);
    sqlite3_bind_double(stmt, 2, amount);
    sqlite3_bind_text(stmt, 3, date.c_str(), -1, SQLITE_STATIC);

    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        std::cerr << "Ошибка выполнения запроса: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_finalize(stmt);
        return false;
    }

    sqlite3_finalize(stmt);
    return true;
}

    static bool updateChargeStatus(sqlite3* db, int chargeId, const std::string& status){
    const char* sql = "UPDATE charges SET status = ? WHERE id = ?;";
    sqlite3_stmt* stmt;

    int rc = sqlite3_prepare(db, sql, -1, &stmt, nullptr);
   if ( rc != SQLITE_OK) {
        std::cerr << "Ошибка подготовки запроса: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    sqlite3_bind_text(stmt, 1, status.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_int(stmt, 2, chargeId);

    rc = sqlite3_step(stmt);
    if(rc != SQLITE_DONE) {
        std::cerr << "Ошибка выполенения запроса: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_finalize(stmt);
        return false;
    }

    sqlite3_finalize(stmt);
    return true;
}
};

int main() {
    sqlite3* db;
    const char* dbFile = "../../db/test.db";

    // Открытие базы данных
    if (sqlite3_open(dbFile, &db) != SQLITE_OK) {
        std::cerr << "Ошибка открытия базы данных: " << sqlite3_errmsg(db) << std::endl;
        return 1;
    }

    // Создание таблиц, если их нет
    const char* createPaymentsTable = "CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, charge_id INTEGER, amount REAL, date TEXT);";
    const char* createChargesTable = "CREATE TABLE IF NOT EXISTS charges (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, amount REAL, status TEXT, date TEXT);";

    if (sqlite3_exec(db, createPaymentsTable, nullptr, nullptr, nullptr) != SQLITE_OK) {
        std::cerr << "Ошибка создания таблицы payments: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        return 1;
    }
    if (sqlite3_exec(db, createChargesTable, nullptr, nullptr, nullptr) != SQLITE_OK) {
        std::cerr << "Ошибка создания таблицы charges: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        return 1;
    }

    // Тестовые данные
    int chargeId = 1;
    double amount = 100.50;
    std::string date = "2023-10-25";
    std::string status = "Paid";

    // Вызов методов
    if (Payment::createPayment(db, chargeId, amount, date)) {
        std::cout << "Оплата успешно создана!" << std::endl;
    }
    if (Payment::updateChargeStatus(db, chargeId, status)) {
        std::cout << "Статус начисления обновлен!" << std::endl;
    }

    sqlite3_close(db);
    return 0;
}
