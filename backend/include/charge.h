#ifndef CHARGE_H
#define CHARGE_H
#include <sqlite3.h>
#include <string>
#include <vector>

struct Charge {
    int id;
    int account_id;
    std::string service_type;
    double tariff;
    double volume;
    double amount;
    std::string period;
    std::string status;
};

class ChargeManager {
private:
    sqlite3* db;
public:
    ChargeManager(sqlite3* database);
    void addCharge(int account_id, const std::string& service_type, double tariff, double volume, const std::string& period);
    std::vector<Charge> listCharges(int account_id, const std::string& period = "");
};

#endif