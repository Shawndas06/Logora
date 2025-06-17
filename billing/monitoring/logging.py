import logging
import logging.handlers
from pathlib import Path
from flask import has_request_context, request, g
from config import Config

LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request context."""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.environ.get('REMOTE_ADDR')
            record.method = request.method
            record.user_agent = request.headers.get('User-Agent', 'Unknown')
            record.request_id = getattr(g, 'request_id', 'unknown')
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.user_agent = None
            record.request_id = None
        
        return super().format(record)

def setup_flask_logging(app):
    """Configure Flask's built-in logging system."""
    
    log_level = logging.DEBUG if Config.DEBUG else logging.INFO
    app.logger.setLevel(log_level)
    
    detailed_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] '
        '[%(request_id)s] [%(method)s %(url)s] [%(remote_addr)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / 'app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    
    error_handler = logging.handlers.RotatingFileHandler(
        filename=LOGS_DIR / 'errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    if Config.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(simple_formatter)
        app.logger.addHandler(console_handler)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    logging.getLogger('flask_cors').setLevel(logging.WARNING)
    
    return app.logger

def log_request_start():
    """Log request start with details."""
    from flask import current_app
    import uuid
    
    g.request_id = str(uuid.uuid4())[:8]
    
    current_app.logger.info(f"Request started - {request.method} {request.path}")

def log_request_end(response):
    """Log request completion."""
    from flask import current_app
    
    current_app.logger.info(
        f"Request completed - {request.method} {request.path} - "
        f"Status: {response.status_code} - "
        f"Size: {response.content_length or 0} bytes"
    )
    return response

def log_database_operation(operation, **kwargs):
    """Log database operations."""
    from flask import current_app
    
    extra_info = " - ".join([f"{k}: {v}" for k, v in kwargs.items()])
    current_app.logger.info(f"DB Operation: {operation} - {extra_info}")

def log_business_event(event, **kwargs):
    """Log business events."""
    from flask import current_app
    
    extra_info = " - ".join([f"{k}: {v}" for k, v in kwargs.items()])
    current_app.logger.info(f"Business Event: {event} - {extra_info}")

def log_error(error, **kwargs):
    """Log errors with context."""
    from flask import current_app
    
    extra_info = " - ".join([f"{k}: {v}" for k, v in kwargs.items()])
    current_app.logger.error(f"Error: {str(error)} - {extra_info}", exc_info=True)

def log_warning(message, **kwargs):
    """Log warnings with context."""
    from flask import current_app
    
    extra_info = " - ".join([f"{k}: {v}" for k, v in kwargs.items()])
    current_app.logger.warning(f"Warning: {message} - {extra_info}")

def log_function_call(func_name=None):
    """Decorator to log function calls."""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from flask import current_app
            
            name = func_name or func.__name__
            current_app.logger.debug(f"Function called: {name}")
            
            try:
                result = func(*args, **kwargs)
                current_app.logger.debug(f"Function completed: {name}")
                return result
            except Exception as e:
                current_app.logger.error(f"Function failed: {name} - {str(e)}")
                raise
        return wrapper
    return decorator
