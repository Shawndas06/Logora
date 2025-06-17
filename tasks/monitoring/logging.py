import logging
import os
from tasks_service.config import APP_LOG_PATH, ERROR_LOG_PATH

def setup_logging():
    os.makedirs(os.path.dirname(APP_LOG_PATH), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(APP_LOG_PATH),
            logging.StreamHandler()
        ]
    )
    
    error_handler = logging.FileHandler(ERROR_LOG_PATH)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(error_handler)