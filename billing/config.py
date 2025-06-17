import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'

class Config:
    DATA_DIR.mkdir(exist_ok=True)

    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(DATA_DIR / 'billing.db'))
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    CORS_SUPPORTS_CREDENTIALS = True
