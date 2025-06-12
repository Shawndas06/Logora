#pragma once

#include <string>
#include <vector>
#include <sqlite3.h>
#include <json.hpp>
#include <stdexcept>

using json = nlohmann::json;

/**
 * @brief Структура для хранения данных платежа
 */
struct Payment {
    int id;
    int account_id;
    double amount;
    std::string payment_date;
    std::string receipt_number;
    std::string status;  // 'completed' или 'pending'
    std::string created_at;
    std::string updated_at;
};

/**
 * @brief Класс для работы с платежами
 */
class PaymentManager {
private:
    sqlite3* db;

    /**
     * @brief Генерирует уникальный номер квитанции
     * @return Уникальный номер квитанции
     */
    std::string generateReceiptNumber();

    /**
     * @brief Преобразует Payment в JSON
     * @param payment Платеж для преобразования
     * @return JSON объект
     */
    json paymentToJson(const Payment& payment);

    /**
     * @brief Проверяет указатель на базу данных
     * @throw std::runtime_error если указатель null
     */
    void checkDatabase() const {
        if (!db) {
            throw std::runtime_error("Database connection is null");
        }
    }

public:
    /**
     * @brief Конструктор
     * @param database Указатель на соединение с базой данных
     * @throw std::invalid_argument если указатель null
     */
    PaymentManager(sqlite3* database);

    /**
     * @brief Деструктор
     */
    ~PaymentManager();

    /**
     * @brief Получить все платежи
     * @param account_id ID счета (опционально)
     * @return JSON массив платежей
     * @throw std::runtime_error при ошибке базы данных
     */
    json getAll(int account_id = 0);

    /**
     * @brief Получить платеж по ID
     * @param id ID платежа
     * @return JSON объект платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    json get(int id);

    /**
     * @brief Создать новый платеж
     * @param account_id ID счета
     * @param amount Сумма
     * @param payment_date Дата платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не существует
     */
    void create(int account_id, double amount, const std::string& payment_date);

    /**
     * @brief Обновить существующий платеж
     * @param id ID платежа
     * @param amount Сумма
     * @param payment_date Дата платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    void update(int id, double amount, const std::string& payment_date);

    /**
     * @brief Удалить платеж
     * @param id ID платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    void remove(int id);

    /**
     * @brief Отметить платеж как выполненный
     * @param id ID платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    void markCompleted(int id);

    /**
     * @brief Отметить платеж как ожидающий
     * @param id ID платежа
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    void markPending(int id);

    /**
     * @brief Получить платежи за период
     * @param start_date Дата начала периода
     * @param end_date Дата окончания периода
     * @return JSON массив платежей
     * @throw std::runtime_error при ошибке базы данных
     */
    json getPaymentsByPeriod(const std::string& start_date, const std::string& end_date);

    /**
     * @brief Получить общую сумму платежей
     * @param account_id ID счета
     * @return Общая сумма платежей
     * @throw std::runtime_error при ошибке базы данных
     */
    double getTotalPayments(int account_id);

    /**
     * @brief Получить квитанцию по ID платежа
     * @param id ID платежа
     * @return JSON объект квитанции
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если платеж не найден
     */
    json getPaymentReceipt(int id);
};