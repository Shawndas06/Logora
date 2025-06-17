from database.connection import get_db

def init_db():
    """Просто проксирует init из connection."""
    from database.connection import init_db as _init
    _init()
