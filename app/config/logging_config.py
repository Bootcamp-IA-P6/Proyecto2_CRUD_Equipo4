import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)

    # Evita duplicar handlers (MUY importante en FastAPI)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5_000_000,  # 5 MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
