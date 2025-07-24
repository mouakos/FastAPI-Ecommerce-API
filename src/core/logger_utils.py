# src/core/logger_utils.py
import logging


class AppLogger:
    def __init__(self, name: str = __name__):
        self._logger = logging.getLogger(name)

    def info(self, message: str, **kwargs):
        self._logger.info(message, extra=kwargs or None)

    def warning(self, message: str, **kwargs):
        self._logger.warning(message, extra=kwargs or None)

    def error(self, message: str, **kwargs):
        self._logger.error(message, extra=kwargs or None)

    def debug(self, message: str, **kwargs):
        self._logger.debug(message, extra=kwargs or None)
