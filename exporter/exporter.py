import logging
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import generate_latest

logger = logging.getLogger(__package__)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        """
        Handle HTTP GET requests.

        If the request path is "/metrics", retrieves metrics from the associated metrics server,
        acquires a lock to ensure thread safety, and returns the metrics with a 200 OK response
        and appropriate content type. For any other path, responds with a 404 Not Found.

        Returns:
            None
        """
        if self.path == "/metrics":
            # Get metrics from server instance
            metrics_server = self.server.metrics_server  # type: Exporter
            with metrics_server.lock:
                metrics = metrics_server.metrics

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(metrics)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format: str, *args) -> None:
        """
        Override to supress redundant log.
        """
        pass


class Exporter:
    def __init__(self, registry, polling_interval: int) -> None:
        """
        Args:
            registry: The metrics registry to use for collecting and exporting metrics.
            polling_interval (int): The interval, in seconds, at which metrics are collected.

        Attributes:
            registry: Stores the provided metrics registry.
            polling_interval (int): The interval for polling metrics.
            metrics (bytes): Cached metrics data in bytes.
            lock (threading.Lock): Lock to synchronize access to metrics.
            _http_server: Reference to the HTTP server instance (initialized as None).
            _collection_thread: Reference to the background collection thread (initialized as None).
            _timestamp (float): Timestamp of the last metrics collection.
        """
        self.registry = registry
        self.polling_interval = polling_interval

        self.metrics = b""
        self.lock = threading.Lock()

        self._http_server = None
        self._collection_thread = None
        self._timestamp = time.time()

    def start_collection_thread(self) -> None:
        """
        Start the collection thread that periodically updates metrics.
        """

        def collect_metrics():
            while True:
                try:
                    with self.lock:
                        self.metrics = generate_latest(self.registry)
                except Exception as e:
                    logger.error(
                        "There was an error collecting metrics: %s", e, exc_info=True
                    )
                time.sleep(self.polling_interval)

        self._collection_thread = threading.Thread(
            target=collect_metrics, daemon=True, name="metrics-collector"
        )
        logger.info("Start metrics collection thread...")
        self._collection_thread.start()

    def serve_metrics(self, host: str, port: int) -> None:
        """
        Start the HTTP server to serve metrics

        Args:
            host (str): Host address to serve metrics on
            port (int): Port number to serve metrics on

        Raises:
            TypeError: If parameters are of wrong type
            ValueError: If port is not in valid range
            OSError: If server cannot bind to the specified host:port
        """
        # Start the collection thread
        self.start_collection_thread()

        try:
            # Create HTTP server
            self._http_server = HTTPServer((host, port), MetricsHandler)
            # Add reference to this instance so handler can access metrics
            self._http_server.metrics_server = self  # type: ignore

            logger.info("Starting metrics server on http://%s:%s/metrics", host, port)
            self._http_server.serve_forever()

        except socket.error as e:
            logger.error("Failed to start metrics server: %s", e, exc_info=True)
            raise
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt...")
        except Exception as e:
            logger.error("Unexpected error serving metrics: %s", e, exc_info=True)
            raise
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Shutdown the metrics server."""
        logger.info("Shutting down exporter...")

        # Shutdown HTTP server if it exists
        if self._http_server:
            try:
                self._http_server.shutdown()
            except Exception as e:
                logger.error("Error shutting down HTTP server: %s", e, exc_info=True)
            finally:
                self._http_server = None

        # Clear thread reference
        self._collection_thread = None

        logger.info("Shutdown complete")
