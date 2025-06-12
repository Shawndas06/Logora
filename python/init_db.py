import sqlite3
import os

def init_db():
    # Путь к файлу базы данных
    db_path = "/app/db/logora.sqlite"
    
    # Удаляем существующую базу данных, если она есть
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Создаем новую базу данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Читаем и выполняем SQL-скрипт схемы
    with open("/app/db/schema.sql", 'r') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)
    
    # Читаем и выполняем SQL-скрипт с тестовыми данными
    with open("/app/db/test_data.sql", 'r') as f:
        test_data = f.read()
        cursor.executescript(test_data)
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print("База данных успешно инициализирована")

if __name__ == "__main__":
    init_db() 