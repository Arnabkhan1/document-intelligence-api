
import logging
import logging.config

from dia.core.config import get_settings


def setup_logging() -> None:
    """
    Configure centralized application logging.
    """

    settings = get_settings()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "%(name)s | "
                    "%(message)s"
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "standard",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.log_level,
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named application logger.
    """
    return logging.getLogger(name)
