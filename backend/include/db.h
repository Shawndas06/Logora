#ifndef DB_H
#define DB_H
#include <sqlite3.h>
#include <string>

class Database {
private:
    sqlite3* db;
public:
    Database(const std::string& db_name);
    ~Database();
    sqlite3* getDb() const;
};

#endif