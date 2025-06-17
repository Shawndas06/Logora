import os
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

def prepare_dirs():
    """Create receipts and qrcodes directories if they don't exist."""
    try:
        os.makedirs(Config.RECEIPTS_DIR, exist_ok=True)
        os.makedirs(Config.QRCODES_DIR, exist_ok=True)
        logger.info("Receipts and QR code directories prepared successfully.")
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        raise

def get_receipt_path(account_id, period=None):
    """Generate the file path for a receipt PDF."""
    if period is None:
        period = datetime.now().strftime("%Y%m")
    filename = f"ACC{account_id:03d}_{period}.pdf"
    path = os.path.join(Config.RECEIPTS_DIR, filename)
    return path

def get_qr_path(account_id, period=None):
    """Generate the file path for a QR code image."""
    if period is None:
        period = datetime.now().strftime("%Y%m")
    filename = f"ACC{account_id:03d}_{period}_qr.png"
    path = os.path.join(Config.QRCODES_DIR, filename)
    return path