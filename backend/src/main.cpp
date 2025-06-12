#include "../include/db.h"
#include "../include/account.h"
#include "../include/charge.h"
#include "../include/payments.h"
#include "../include/api.h"
#include <iostream>

int main() {
    try {
        Database db("../../db/schema.sql");
        AccountManager accountManager(db.getDb());
        ChargeManager chargeManager(db.getDb());
        PaymentManager paymentManager(db.getDb());
        ApiController api(accountManager, chargeManager, paymentManager, "http://0.0.0.0:8080"); //Или http://localhost:8080
        api.start();
        std::cout << "Сервер запущен на http://0.0.0.0:8080. Нажмите Enter для остановки.\n"; //И здесь
        std::cin.get();
    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << std::endl;
        return 1;
    }
    return 0;
}