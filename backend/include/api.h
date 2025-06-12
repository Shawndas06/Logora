#ifndef API_H
#define API_H
#include "account.h"
#include "charge.h"
#include "payments.h"
#include <cpprest/http_listener.h>

class ApiController {
private:
    AccountManager& accountManager;
    ChargeManager& chargeManager;
    PaymentManager& paymentManager;
    web::http::experimental::listener::http_listener listener;
public:
    ApiController(AccountManager& am, ChargeManager& cm, PaymentManager& pm, const std::string& uri);
    void start();
};

#endif