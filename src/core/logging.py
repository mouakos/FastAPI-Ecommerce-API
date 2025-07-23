import logging
from enum import StrEnum

LOG_FORMAT_DEBUG = (
    "%(levelname)s - %(message)s - %(pathname)s - %(funcName)s - %(lineno)d"
)


class LogLevel(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def setup_logging(level: str = LogLevel.error) -> None:
    log_level = str(level).upper()
    log_levels = [level.value for level in LogLevel]

    if log_level not in log_levels:
        logging.basicConfig(level=logging.error)
        return

    if log_level == LogLevel.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)
