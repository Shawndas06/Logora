#ifndef PAYMENTS_H
#define PAYMENTS_H
#include <sqlite3.h>
#include <string>
#include <vector>

struct Payment {
    int id;
    int charge_id;
    double amount;
    std::string payment_date;
};

class PaymentManager {
private:
    sqlite3* db;
public:
    PaymentManager(sqlite3* database);
    void makePayment(int charge_id, double amount);
    void payAllCharges(int account_id, const std::string& period);
    std::vector<Payment> listPayments(int account_id);
};

#endif