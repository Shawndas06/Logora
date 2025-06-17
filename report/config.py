import os
from pathlib import Path

# Определяем пути
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"


class Config:
    # Создаем папки
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # База данных
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(DATA_DIR / "reports.db"))

    # Настройки Flask
    HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
    PORT = int(os.environ.get("FLASK_PORT", 5000))
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")

    # Пути
    REPORTS_DIR_PATH = str(REPORTS_DIR)
    LOGS_DIR_PATH = str(LOGS_DIR)

    # CORS
    CORS_SUPPORTS_CREDENTIALS = True
