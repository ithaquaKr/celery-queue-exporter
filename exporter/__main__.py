"""
Main Entrypoint.
"""

import logging

from prometheus_client.core import REGISTRY

from exporter.collector import CQCollector
from exporter.configs import (
    EXPORTER_HOST,
    EXPORTER_POLLING_INTERVAL,
    EXPORTER_PORT,
    LOG_DATEFMT,
    LOG_FORMAT,
    LOG_LEVEL,
)
from exporter.exporter import Exporter


logger = logging.getLogger(__package__)


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATEFMT,
    )


def main():
    setup_logging()
    logger.info("Exporter is starting ...")

    REGISTRY.register(CQCollector("redis", {}))
    Exporter(
        REGISTRY,
        int(EXPORTER_POLLING_INTERVAL),
    ).serve_metrics(EXPORTER_HOST, int(EXPORTER_PORT))


if __name__ == "__main__":
    main()
