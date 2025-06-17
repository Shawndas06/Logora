import os

class Config:
    DATABASE_PATH = os.getenv('PAYMENTS_DATABASE_PATH', 'data/payments.db')
    BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://billing:5000')

    CORS_SUPPORTS_CREDENTIALS = True
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true')
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))


DB_PATH = 'payments_new/data/payment.db'
BILLING_URL = 'http://charges-service:5003/api/billing/complete'
