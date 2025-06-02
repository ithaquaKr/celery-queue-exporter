"""A Prometheus exporter for monitoring Celery queue metrics."""

from celery_queue_exporter.logging_config import setup_logging

__version__ = "0.1.0"
__author__ = "ITHALab"
__email__ = "info@ithalab.com"

# Set up logging when the package is imported
setup_logging() 