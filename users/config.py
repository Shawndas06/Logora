import os

class Config:
    DATABASE_PATH = os.getenv('USERS_DATABASE_PATH', 'data/users.db')

    CORS_SUPPORTS_CREDENTIALS = True
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true')
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
