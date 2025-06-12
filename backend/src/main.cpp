#include <iostream>
#include <string>
#include <httplib.h>
#include <json.hpp>
#include "../include/accounts.h"
#include "../include/charges.h"
#include "../include/payments.h"
#include <sqlite3.h>
#include <filesystem>
#include <fstream>
#include <cstdlib>
#include <signal.h>
#include <chrono>
#include <map>
#include <mutex>
#include <sstream>
#include <iomanip>

using json = nlohmann::json;
using namespace httplib;

// Глобальные переменные
sqlite3* db = nullptr;
AccountManager* accountManager = nullptr;
ChargeManager* chargeManager = nullptr;
PaymentManager* paymentManager = nullptr;
bool running = true;

// Структура для rate limiting
struct RateLimit {
    int requests;
    std::chrono::system_clock::time_point reset_time;
};

// Rate limiting
std::map<std::string, RateLimit> rate_limits;
std::mutex rate_limit_mutex;
const int MAX_REQUESTS = 100;
const int WINDOW_SECONDS = 60;

// Логирование
void logRequest(const Request& req, const Response& res) {
    auto now = std::chrono::system_clock::now();
    auto now_time_t = std::chrono::system_clock::to_time_t(now);
    auto now_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_time_t), "%Y-%m-%d %H:%M:%S")
       << '.' << std::setfill('0') << std::setw(3) << now_ms.count()
       << " " << req.method << " " << req.path
       << " " << res.status
       << " " << req.remote_addr
       << " " << req.get_header_value("User-Agent");
    
    std::cout << ss.str() << std::endl;
}

// Проверка rate limit
bool checkRateLimit(const std::string& ip) {
    std::lock_guard<std::mutex> lock(rate_limit_mutex);
    auto now = std::chrono::system_clock::now();
    
    auto it = rate_limits.find(ip);
    if (it == rate_limits.end() || 
        now > it->second.reset_time) {
        rate_limits[ip] = {1, now + std::chrono::seconds(WINDOW_SECONDS)};
        return true;
    }
    
    if (it->second.requests >= MAX_REQUESTS) {
        return false;
    }
    
    it->second.requests++;
    return true;
}

// Валидация JSON
bool validateJson(const json& data, const std::vector<std::string>& required_fields) {
    for (const auto& field : required_fields) {
        if (!data.contains(field)) {
            return false;
        }
    }
    return true;
}

// Обработчик сигналов
void signalHandler(int signum) {
    std::cout << "Received signal " << signum << std::endl;
    running = false;
}

// Получение пути к базе данных из переменной окружения
std::string getDatabasePath() {
    const char* dbPath = std::getenv("DB_PATH");
    if (dbPath) {
        return dbPath;
    }
    return "/app/db/logora.sqlite";
}

// Инициализация базы данных
bool initDatabase() {
    std::string dbPath = getDatabasePath();
    std::cout << "Opening database at: " << dbPath << std::endl;
    
    if (sqlite3_open(dbPath.c_str(), &db) != SQLITE_OK) {
        std::cerr << "Ошибка открытия базы данных: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }

    // Чтение и выполнение schema.sql
    std::string schemaPath = "/app/db/schema.sql";
    std::cout << "Reading schema from: " << schemaPath << std::endl;
    
    std::ifstream schemaFile(schemaPath);
    if (!schemaFile.is_open()) {
        std::cerr << "Ошибка открытия файла schema.sql" << std::endl;
        return false;
    }

    std::string schema((std::istreambuf_iterator<char>(schemaFile)),
                        std::istreambuf_iterator<char>());
    schemaFile.close();

    char* errMsg = nullptr;
    if (sqlite3_exec(db, schema.c_str(), nullptr, nullptr, &errMsg) != SQLITE_OK) {
        std::cerr << "Ошибка выполнения schema.sql: " << errMsg << std::endl;
        sqlite3_free(errMsg);
        return false;
    }

    std::cout << "Database initialized successfully" << std::endl;
    return true;
}

// Очистка ресурсов
void cleanup() {
    delete accountManager;
    delete chargeManager;
    delete paymentManager;
    if (db) {
        sqlite3_close(db);
    }
}

int main() {
    // Установка обработчиков сигналов
    signal(SIGINT, signalHandler);
    signal(SIGTERM, signalHandler);

    // Инициализация базы данных
    if (!initDatabase()) {
        return 1;
    }

    // Создание менеджеров
    accountManager = new AccountManager(db);
    chargeManager = new ChargeManager(db);
    paymentManager = new PaymentManager(db);

    // Настройка сервера
    Server svr;
    
    // Настройка CORS
    svr.set_default_headers({
        {"Access-Control-Allow-Origin", "*"},
        {"Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"},
        {"Access-Control-Allow-Headers", "Content-Type"}
    });

    // Middleware для логирования и rate limiting
    svr.set_logger([](const Request& req, const Response& res) {
        logRequest(req, res);
    });

    // Обработка OPTIONS запросов
    svr.Options(".*", [](const Request&, Response& res) {
        res.set_header("Access-Control-Allow-Origin", "*");
        res.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        res.set_header("Access-Control-Allow-Headers", "Content-Type");
    });

    // Health check endpoint
    svr.Get("/health", [](const Request&, Response& res) {
        res.set_content(json{{"status", "healthy"}}.dump(), "application/json");
    });

    // API для счетов
    svr.Get("/api/accounts", [&](const Request& req, Response& res) {
        if (!checkRateLimit(req.remote_addr)) {
            res.status = 429;
            res.set_content(json{{"error", "Too many requests"}}.dump(), "application/json");
            return;
        }

        try {
            res.set_content(accountManager->getAll().dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Get("/api/accounts/:id", [&](const Request& req, Response& res) {
        if (!checkRateLimit(req.remote_addr)) {
            res.status = 429;
            res.set_content(json{{"error", "Too many requests"}}.dump(), "application/json");
            return;
        }

        try {
            int id = std::stoi(req.path_params.at("id"));
            res.set_content(accountManager->get(id).dump(), "application/json");
        } catch (const std::invalid_argument& e) {
            res.status = 400;
            res.set_content(json{{"error", "Invalid account ID"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Post("/api/accounts", [&](const Request& req, Response& res) {
        if (!checkRateLimit(req.remote_addr)) {
            res.status = 429;
            res.set_content(json{{"error", "Too many requests"}}.dump(), "application/json");
            return;
        }

        try {
            auto data = json::parse(req.body);
            if (!validateJson(data, {"number", "name", "address"})) {
                res.status = 400;
                res.set_content(json{{"error", "Missing required fields"}}.dump(), "application/json");
                return;
            }

            accountManager->create(data["number"], data["name"], data["address"]);
            res.status = 201;
            res.set_content(json{{"message", "Account created successfully"}}.dump(), "application/json");
        } catch (const json::parse_error& e) {
            res.status = 400;
            res.set_content(json{{"error", "Invalid JSON"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Put("/api/accounts/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            json data = json::parse(req.body);
            accountManager->update(
                id,
                data["number"].get<std::string>(),
                data["name"].get<std::string>(),
                data["address"].get<std::string>()
            );
            res.status = 200;
            res.set_content(json{{"message", "Account updated"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Delete("/api/accounts/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            accountManager->remove(id);
            res.status = 200;
            res.set_content(json{{"message", "Account deleted"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    // API для начислений
    svr.Get("/api/charges", [&](const Request& req, Response& res) {
        try {
            int account_id = 0;
            if (req.has_param("account_id")) {
                account_id = std::stoi(req.get_param_value("account_id"));
            }
            res.set_content(chargeManager->getAll(account_id).dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Post("/api/charges", [&](const Request& req, Response& res) {
        try {
            json data = json::parse(req.body);
            chargeManager->create(
                data["account_id"].get<int>(),
                data["service"].get<std::string>(),
                data["amount"].get<double>(),
                data["start_date"].get<std::string>(),
                data["end_date"].get<std::string>()
            );
            res.status = 201;
            res.set_content(json{{"message", "Charge created"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Get("/api/charges/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            res.set_content(chargeManager->get(id).dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Put("/api/charges/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            json data = json::parse(req.body);
            chargeManager->update(
                id,
                data["service"].get<std::string>(),
                data["amount"].get<double>(),
                data["start_date"].get<std::string>(),
                data["end_date"].get<std::string>()
            );
            res.status = 200;
            res.set_content(json{{"message", "Charge updated"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Delete("/api/charges/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            chargeManager->remove(id);
            res.status = 200;
            res.set_content(json{{"message", "Charge deleted"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    // API для платежей
    svr.Get("/api/payments", [&](const Request& req, Response& res) {
        try {
            int account_id = 0;
            if (req.has_param("account_id")) {
                account_id = std::stoi(req.get_param_value("account_id"));
            }
            res.set_content(paymentManager->getAll(account_id).dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Post("/api/payments", [&](const Request& req, Response& res) {
        try {
            json data = json::parse(req.body);
            paymentManager->create(
                data["account_id"].get<int>(),
                data["amount"].get<double>(),
                data["method"].get<std::string>()
            );
            res.status = 201;
            res.set_content(json{{"message", "Payment created"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Get("/api/payments/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            res.set_content(paymentManager->get(id).dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Put("/api/payments/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            json data = json::parse(req.body);
            paymentManager->update(
                id,
                data["amount"].get<double>(),
                data["method"].get<std::string>()
            );
            res.status = 200;
            res.set_content(json{{"message", "Payment updated"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    svr.Delete("/api/payments/(\\d+)", [&](const Request& req, Response& res) {
        try {
            int id = std::stoi(req.matches[1]);
            paymentManager->remove(id);
            res.status = 200;
            res.set_content(json{{"message", "Payment deleted"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 500;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });

    // Запуск сервера
    std::cout << "Server starting..." << std::endl;
    svr.listen("0.0.0.0", 8080);

    // Очистка при завершении
    cleanup();
    return 0;
}