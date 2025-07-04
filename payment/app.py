from flask import Flask
from flask_cors import CORS
from config import Config
from routes.payments_routes import payment_bp
from database.connection import init_database

def create_app():
    app = Flask(__name__)

    CORS(app, supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)

    init_database()

    app.register_blueprint(payment_bp, url_prefix='')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT)
