#include "api.h"
#include <cpprest/json.h>
#include <cpprest/uri.h>

using namespace web;
using namespace web::http;
using namespace web::http::experimental::listener;

ApiController::ApiController(AccountManager& am, ChargeManager& cm, PaymentManager& pm, const std::string& uri)
    : accountManager(am), chargeManager(cm), paymentManager(pm), listener(uri) {
    listener.support(methods::POST, [this](http_request req) {
        try {
            if (req.relative_uri().path() == "/accounts") {
                req.extract_json().then([this, req](json::value body) {
                    try {
                        int user_id = body.at("user_id").as_integer();
                        std::string number = body.at("number").as_string();
                        std::string name = body.at("name").as_string();
                        std::string address = body.at("address").as_string();
                        double area = body.at("area").as_double();
                        int residents = body.at("residents").as_integer();
                        std::string company = body.at("company").as_string();
                        accountManager.createAccount(user_id, number, name, address, area, residents, company);
                        req.reply(status_codes::Created, json::value::object());
                    } catch (const std::exception& e) {
                        req.reply(status_codes::BadRequest, json::value::string(e.what()));
                    }
                }).wait();
            } else if (req.relative_uri().path() == "/charges") {
                req.extract_json().then([this, req](json::value body) {
                    try {
                        int account_id = body.at("account_id").as_integer();
                        std::string service_type = body.at("service_type").as_string();
                        double tariff = body.at("tariff").as_double();
                        double volume = body.at("volume").as_double();
                        std::string period = body.at("period").as_string();
                        chargeManager.addCharge(account_id, service_type, tariff, volume, period);
                        req.reply(status_codes::Created, json::value::object());
                    } catch (const std::exception& e) {
                        req.reply(status_codes::BadRequest, json::value::string(e.what()));
                    }
                }).wait();
            } else if (req.relative_uri().path() == "/payments") {
                req.extract_json().then([this, req](json::value body) {
                    try {
                        int charge_id = body.at("charge_id").as_integer();
                        double amount = body.at("amount").as_double();
                        paymentManager.makePayment(charge_id, amount);
                        req.reply(status_codes::Created, json::value::object());
                    } catch (const std::exception& e) {
                        req.reply(status_codes::BadRequest, json::value::string(e.what()));
                    }
                }).wait();
            } else if (req.relative_uri().path() == "/pay_all") {
                req.extract_json().then([this, req](json::value body) {
                    try {
                        int account_id = body.at("account_id").as_integer();
                        std::string period = body.at("period").as_string();
                        paymentManager.payAllCharges(account_id, period);
                        req.reply(status_codes::OK, json::value::object());
                    } catch (const std::exception& e) {
                        req.reply(status_codes::BadRequest, json::value::string(e.what()));
                    }
                }).wait();
            } else {
                req.reply(status_codes::NotFound);
            }
        } catch (const std::exception& e) {
            req.reply(status_codes::InternalError, json::value::string(e.what()));
        }
    });

    listener.support(methods::GET, [this](http_request req) {
        try {
            if (req.relative_uri().path() == "/accounts") {
                auto query = uri::split_query(req.relative_uri().query());
                if (query.find("user_id") == query.end()) {
                    req.reply(status_codes::BadRequest, json::value::string("user_id is required"));
                    return;
                }
                int user_id = std::stoi(query["user_id"]);
                auto accounts = accountManager.listAccounts(user_id);
                json::value response = json::value::array();
                for (size_t i = 0; i < accounts.size(); ++i) {
                    json::value acc;
                    acc["id"] = json::value::number(accounts[i].id);
                    acc["user_id"] = json::value::number(accounts[i].user_id);
                    acc["number"] = json::value::string(accounts[i].number);
                    acc["name"] = json::value::string(accounts[i].name);
                    acc["address"] = json::value::string(accounts[i].address);
                    acc["area"] = json::value::number(accounts[i].area);
                    acc["residents"] = json::value::number(accounts[i].residents);
                    acc["company"] = json::value::string(accounts[i].company);
                    response[i] = acc;
                }
                req.reply(status_codes::OK, response);
            } else if (req.relative_uri().path() == "/charges") {
                auto query = uri::split_query(req.relative_uri().query());
                if (query.find("account_id") == query.end()) {
                    req.reply(status_codes::BadRequest, json::value::string("account_id is required"));
                    return;
                }
                int account_id = std::stoi(query["account_id"]);
                std::string period = query.find("period") != query.end() ? query["period"] : "";
                auto charges = chargeManager.listCharges(account_id, period);
                json::value response = json::value::array();
                for (size_t i = 0; i < charges.size(); ++i) {
                    json::value charge;
                    charge["id"] = json::value::number(charges[i].id);
                    charge["account_id"] = json::value::number(charges[i].account_id);
                    charge["service_type"] = json::value::string(charges[i].service_type);
                    charge["tariff"] = json::value::number(charges[i].tariff);
                    charge["volume"] = json::value::number(charges[i].volume);
                    charge["amount"] = json::value::number(charges[i].amount);
                    charge["period"] = json::value::string(charges[i].period);
                    charge["status"] = json::value::string(charges[i].status);
                    response[i] = charge;
                }
                req.reply(status_codes::OK, response);
            } else if (req.relative_uri().path() == "/payments") {
                auto query = uri::split_query(req.relative_uri().query());
                if (query.find("account_id") == query.end()) {
                    req.reply(status_codes::BadRequest, json::value::string("account_id is required"));
                    return;
                }
                int account_id = std::stoi(query["account_id"]);
                auto payments = paymentManager.listPayments(account_id);
                json::value response = json::value::array();
                for (size_t i = 0; i < payments.size(); ++i) {
                    json::value payment;
                    payment["id"] = json::value::number(payments[i].id);
                    payment["charge_id"] = json::value::number(payments[i].charge_id);
                    payment["amount"] = json::value::number(payments[i].amount);
                    payment["payment_date"] = json::value::string(payments[i].payment_date);
                    response[i] = payment;
                }
                req.reply(status_codes::OK, response);
            } else {
                req.reply(status_codes::NotFound);
            }
        } catch (const std::exception& e) {
            req.reply(status_codes::InternalError, json::value::string(e.what()));
        }
    });

    listener.support(methods::PUT, [this](http_request req) {
        try {
            if (req.relative_uri().path().find("/accounts/") == 0) {
                int id = std::stoi(req.relative_uri().path().substr(10));
                req.extract_json().then([this, req, id](json::value body) {
                    try {
                        std::string number = body.at("number").as_string();
                        std::string name = body.at("name").as_string();
                        std::string address = body.at("address").as_string();
                        double area = body.at("area").as_double();
                        int residents = body.at("residents").as_integer();
                        std::string company = body.at("company").as_string();
                        accountManager.updateAccount(id, number, name, address, area, residents, company);
                        req.reply(status_codes::OK, json::value::object());
                    } catch (const std::exception& e) {
                        req.reply(status_codes::BadRequest, json::value::string(e.what()));
                    }
                }).wait();
            } else {
                req.reply(status_codes::NotFound);
            }
        } catch (const std::exception& e) {
            req.reply(status_codes::InternalError, json::value::string(e.what()));
        }
    });

    listener.support(methods::DEL, [this](http_request req) {
        try {
            if (req.relative_uri().path().find("/accounts/") == 0) {
                int id = std::stoi(req.relative_uri().path().substr(10));
                accountManager.deleteAccount(id);
                req.reply(status_codes::OK, json::value::object());
            } else {
                req.reply(status_codes::NotFound);
            }
        } catch (const std::exception& e) {
            req.reply(status_codes::InternalError, json::value::string(e.what()));
        }
    });
}

void ApiController::start() {
    try {
        listener.open().wait();
    } catch (const std::exception& e) {
        throw std::runtime_error("Ошибка запуска сервера: " + std::string(e.what()));
    }
}