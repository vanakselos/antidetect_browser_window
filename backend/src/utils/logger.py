import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    _instance: Optional[logging.Logger] = None

    @staticmethod
    def setup_logger() -> logging.Logger:
        if Logger._instance is None:
            # Create logs directory if it doesn't exist
            if not os.path.exists('logs'):
                os.makedirs('logs')

            # Create logger
            logger = logging.getLogger('AntiDetectBrowser')
            logger.setLevel(logging.DEBUG)

            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s'
            )

            # File handler
            current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_handler = logging.FileHandler(
                f'logs/antidetect_{current_time}.log'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)

            # Add handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

            Logger._instance = logger

        return Logger._instance


def get_logger(name: str = None) -> logging.Logger:
    if Logger._instance is None:
        Logger.setup_logger()

    if name:
        return logging.getLogger(f'AntiDetectBrowser.{name}')
    return Logger._instance


# For backward compatibility
setup_logger = Logger.setup_logger