#include "db.h"
#include <stdexcept>

Database::Database(const std::string& db_name) {
    if (sqlite3_open(db_name.c_str(), &db) != SQLITE_OK) {
        throw std::runtime_error("Ошибка открытия базы данных: " + std::string(sqlite3_errmsg(db)));
    }
}

Database::~Database() {
    sqlite3_close(db);
}

sqlite3* Database::getDb() const {
    return db;
}