import logging
import sys


def setup_logging():
    """Configure logging for the application"""
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("Config Management APP")
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)


def get_logger() -> logging.Logger:
    return logging.getLogger("Config Management APP")
