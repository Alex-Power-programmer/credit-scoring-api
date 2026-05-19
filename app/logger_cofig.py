import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # INFO, WARNING, ERROR, CRITICAL

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    info_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=5*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    info_handler.setFormatter(log_format)
    info_handler.setLevel(logging.INFO) # INFO, WARNING, ERROR, CRITICAL

    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=2*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR) # ERROR and CRITICAL
    error_handler.setFormatter(log_format)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)









