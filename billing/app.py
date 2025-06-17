import uuid
from flask import Flask, g
from flask_cors import CORS
from config import Config
from database.connection import init_database
from monitoring.logging import log_request_end, log_request_start, setup_flask_logging
from routes.billing_routes import billing_bp

def create_app():
    app = Flask(__name__)

    CORS(app, supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS)

    logger = setup_flask_logging(app)
    
    init_database()
    logger.info("Database initialized successfully")

    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())[:8]
        log_request_start()
    
    @app.after_request
    def after_request(response):
        return log_request_end(response)

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"404 error: {error}")
        return {
            "success": False,
            "message": "Endpoint not found"
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 error: {error}", exc_info=True)
        return {
            "success": False,
            "message": "Internal server error"
        }, 500
    
    app.register_blueprint(billing_bp)

    logger.info("API application created successfully")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST, 
        port=Config.PORT, 
        debug=Config.DEBUG
    )
