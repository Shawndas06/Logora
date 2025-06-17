import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Хранить БД в папке data/tasks.db
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'tasks.db')

# Пути для логов
LOG_DIR = os.path.join(BASE_DIR, 'logs')
APP_LOG_PATH = os.path.join(LOG_DIR, 'app.log')
ERROR_LOG_PATH = os.path.join(LOG_DIR, 'errors.log')

class Config:
    DATABASE_PATH = os.getenv('USERS_DATABASE_PATH', 'data/users.db')

    CORS_SUPPORTS_CREDENTIALS = True
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true')
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
