#!/bin/bash

# Переходим в директорию с Python файлами
cd /app/python

# Инициализация базы данных
python init_db.py

# Запуск Flask приложения
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000 