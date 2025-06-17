import logging as _log
import logging.handlers as _handlers
from pathlib import Path
from flask import has_request_context, request, g, current_app
from config import Config
import uuid

# Папка logs/ рядом с project root
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

class RequestFormatter(_log.Formatter):
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
    """Configure Flask logging with rotating files and optional console."""
    level = _log.DEBUG if Config.DEBUG else _log.INFO
    app.logger.setLevel(level)

    detailed_fmt = RequestFormatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] '
        '[%(request_id)s] [%(method)s %(url)s] [%(remote_addr)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_fmt = _log.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    fh = _handlers.RotatingFileHandler(LOGS_DIR / 'app.log', maxBytes=10*1024*1024, backupCount=5)
    fh.setLevel(_log.INFO)
    fh.setFormatter(detailed_fmt)

    # Error handler
    eh = _handlers.RotatingFileHandler(LOGS_DIR / 'errors.log', maxBytes=10*1024*1024, backupCount=5)
    eh.setLevel(_log.ERROR)
    eh.setFormatter(detailed_fmt)

    app.logger.addHandler(fh)
    app.logger.addHandler(eh)

    if Config.DEBUG:
        ch = _log.StreamHandler()
        ch.setLevel(_log.DEBUG)
        ch.setFormatter(simple_fmt)
        app.logger.addHandler(ch)

    # suppress overly verbose CORS logs
    _log.getLogger('flask_cors').setLevel(_log.WARNING)
    return app.logger

def log_request_start():
    """Log start of a request, assign request_id."""
    g.request_id = str(uuid.uuid4())[:8]
    current_app.logger.info(f"Request started - {request.method} {request.path}")

def log_request_end(response):
    """Log end of a request."""
    current_app.logger.info(
        f"Request completed - {request.method} {request.path} - "
        f"Status: {response.status_code} - Size: {response.content_length or 0} bytes"
    )
    return response

def log_database_operation(operation, **kwargs):
    """Log a database operation."""
    extra = " - ".join(f"{k}: {v}" for k, v in kwargs.items())
    current_app.logger.info(f"DB Operation: {operation} - {extra}")

def log_business_event(event, **kwargs):
    """Log a business event."""
    extra = " - ".join(f"{k}: {v}" for k, v in kwargs.items())
    current_app.logger.info(f"Business Event: {event} - {extra}")

def log_error(error, **kwargs):
    """Log an error with context."""
    extra = " - ".join(f"{k}: {v}" for k, v in kwargs.items())
    current_app.logger.error(f"Error: {str(error)} - {extra}", exc_info=True)

def log_warning(message, **kwargs):
    """Log a warning with context."""
    extra = " - ".join(f"{k}: {v}" for k, v in kwargs.items())
    current_app.logger.warning(f"Warning: {message} - {extra}")

def log_function_call(func):
    """Decorator to log entry/exit of a function."""
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_app.logger.debug(f"Function called: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            current_app.logger.debug(f"Function completed: {func.__name__}")
            return result
        except Exception as e:
            current_app.logger.error(f"Function failed: {func.__name__} - {e}")
            raise
    return wrapper
