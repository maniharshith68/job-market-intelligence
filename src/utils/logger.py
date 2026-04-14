# src/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module.
    Logs to both console and a rotating file in logs/.
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger  # Avoid duplicate handlers

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Rotating file handler per module
    log_file = f"logs/{module_name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
