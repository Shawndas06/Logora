import os

class Config:
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    ACCOUNT_SERVICE_URL = os.environ.get('ACCOUNT_SERVICE_URL', 'http://account:5000')
    BILLING_SERVICE_URL = os.environ.get('BILLING_SERVICE_URL', 'http://billing:5000')
    PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://payment:5000')
    USERS_SERVICE_URL = os.environ.get('USERS_SERVICE_URL', 'http://users:5000')
    CORS_SUPPORTS_CREDENTIALS = True
