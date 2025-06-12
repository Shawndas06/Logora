#pragma once

#include <string>
#include <vector>
#include <sqlite3.h>
#include <json.hpp>
#include <stdexcept>

using json = nlohmann::json;

/**
 * @brief Структура для хранения данных начисления
 */
struct Charge {
    int id;
    int account_id;
    std::string service;
    double amount;
    std::string start_date;
    std::string end_date;
    std::string status;  // 'pending' или 'paid'
    std::string created_at;
    std::string updated_at;
};

/**
 * @brief Класс для работы с начислениями
 */
class ChargeManager {
private:
    sqlite3* db;

    /**
     * @brief Преобразует Charge в JSON
     * @param charge Начисление для преобразования
     * @return JSON объект
     */
    json chargeToJson(const Charge& charge);

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
    ChargeManager(sqlite3* database);

    /**
     * @brief Деструктор
     */
    ~ChargeManager();

    /**
     * @brief Получить все начисления
     * @param account_id ID счета (опционально)
     * @return JSON массив начислений
     * @throw std::runtime_error при ошибке базы данных
     */
    json getAll(int account_id = 0);

    /**
     * @brief Получить начисление по ID
     * @param id ID начисления
     * @return JSON объект начисления
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если начисление не найдено
     */
    json get(int id);

    /**
     * @brief Создать новое начисление
     * @param account_id ID счета
     * @param service Услуга
     * @param amount Сумма
     * @param start_date Дата начала
     * @param end_date Дата окончания
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не существует
     */
    void create(int account_id, const std::string& service, double amount,
                const std::string& start_date, const std::string& end_date);

    /**
     * @brief Обновить существующее начисление
     * @param id ID начисления
     * @param service Услуга
     * @param amount Сумма
     * @param start_date Дата начала
     * @param end_date Дата окончания
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если начисление не найдено
     */
    void update(int id, const std::string& service, double amount,
                const std::string& start_date, const std::string& end_date);

    /**
     * @brief Удалить начисление
     * @param id ID начисления
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если начисление не найдено
     */
    void remove(int id);

    /**
     * @brief Отметить начисление как оплаченное
     * @param id ID начисления
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если начисление не найдено
     */
    void markPaid(int id);

    /**
     * @brief Отметить начисление как ожидающее оплаты
     * @param id ID начисления
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если начисление не найдено
     */
    void markPending(int id);

    /**
     * @brief Получить начисления за период
     * @param start_date Дата начала периода
     * @param end_date Дата окончания периода
     * @return JSON массив начислений
     * @throw std::runtime_error при ошибке базы данных
     */
    json getChargesByPeriod(const std::string& start_date, const std::string& end_date);

    /**
     * @brief Получить общую сумму начислений
     * @param account_id ID счета
     * @return Общая сумма начислений
     * @throw std::runtime_error при ошибке базы данных
     */
    double getTotalAmount(int account_id);
};