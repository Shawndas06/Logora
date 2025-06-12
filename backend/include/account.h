#ifndef ACCOUNT_H
#define ACCOUNT_H
#include <string>
#include <vector>
#include <sqlite3.h>

struct Account {
    int id;
    int user_id;
    std::string number;
    std::string name;
    std::string address;
    double area;
    int residents;
    std::string company;
};

class AccountManager {
private:
    sqlite3* db;
    bool validateNumber(const std::string& number) const;
public:
    AccountManager(sqlite3* database);
    void createAccount(int user_id, const std::string& number, const std::string& name,
                      const std::string& address, double area, int residents, const std::string& company);
    std::vector<Account> listAccounts(int user_id);
    void updateAccount(int id, const std::string& number, const std::string& name,
                      const std::string& address, double area, int residents, const std::string& company);
    void deleteAccount(int id);
};

#endif