import logging
import sys


def setup_logging(debug: bool = False):
    """Configures centralized structured logging for the application."""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
