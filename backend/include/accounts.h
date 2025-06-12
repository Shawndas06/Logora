#pragma once

#include <string>
#include <vector>
#include <sqlite3.h>
#include <json.hpp>
#include <stdexcept>

using json = nlohmann::json;

/**
 * @brief Структура для хранения данных счета
 */
struct Account {
    int id;
    std::string number;
    std::string name;
    std::string address;
    std::string status;  // 'active' или 'inactive'
    std::string created_at;
    std::string updated_at;
};

/**
 * @brief Класс для работы со счетами
 */
class AccountManager {
private:
    sqlite3* db;

    /**
     * @brief Преобразует Account в JSON
     * @param account Счет для преобразования
     * @return JSON объект
     */
    json accountToJson(const Account& account);

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
    AccountManager(sqlite3* database);

    /**
     * @brief Деструктор
     */
    ~AccountManager();

    /**
     * @brief Получить все счета
     * @return JSON массив счетов
     * @throw std::runtime_error при ошибке базы данных
     */
    json getAll();

    /**
     * @brief Получить счет по ID
     * @param id ID счета
     * @return JSON объект счета
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не найден
     */
    json get(int id);

    /**
     * @brief Создать новый счет
     * @param number Номер счета
     * @param name Имя владельца
     * @param address Адрес
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если номер счета уже существует
     */
    void create(const std::string& number, const std::string& name, const std::string& address);

    /**
     * @brief Обновить существующий счет
     * @param id ID счета
     * @param number Новый номер счета
     * @param name Новое имя владельца
     * @param address Новый адрес
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не найден
     */
    void update(int id, const std::string& number, const std::string& name, const std::string& address);

    /**
     * @brief Удалить счет
     * @param id ID счета
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не найден
     */
    void remove(int id);

    /**
     * @brief Активировать счет
     * @param id ID счета
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не найден
     */
    void activate(int id);

    /**
     * @brief Деактивировать счет
     * @param id ID счета
     * @throw std::runtime_error при ошибке базы данных
     * @throw std::invalid_argument если счет не найден
     */
    void deactivate(int id);

    /**
     * @brief Получить счета пользователя
     * @param userId ID пользователя
     * @return JSON массив счетов
     * @throw std::runtime_error при ошибке базы данных
     */
    json getAccountsByUser(int userId);

    /**
     * @brief Проверить существование счета
     * @param account_number Номер счета
     * @return true если счет существует, false в противном случае
     * @throw std::runtime_error при ошибке базы данных
     */
    bool accountExists(const std::string& account_number);
};