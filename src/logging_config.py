"""Central logging configuration for Dragon Hunt."""

import logging

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s %(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """Configure consistent application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
