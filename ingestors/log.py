import logging
import os


json_logging = bool(os.getenv("ALEPH_JSON_LOGGING", False))
if json_logging:
    from pythonjsonlogger import jsonlogger


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if json_logging:
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)

    return logger
