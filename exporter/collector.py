import logging
from typing import Any, Dict, Iterable, Optional

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from exporter.brokers import Broker, BrokerFactory

logger = logging.getLogger(__name__)


class CQCollector(Collector):
    """Celery Queue metrics collector for Prometheus."""

    def __init__(
        self,
        broker_type: str,
        broker_config: Dict[str, Any],
    ) -> None:
        """Initialize the collector.

        Args:
            broker_type: Type of broker to use
            broker_config: Configuration for the broker connection
        """
        self._broker: Optional[Broker] = None
        try:
            self._broker = BrokerFactory.create(broker_type, **broker_config)
            self._broker.connect()
        except Exception as e:
            logger.error(f"Failed to initialize broker: {e}", exc_info=True)
            raise

    def collect(self) -> Iterable[Metric]:
        """Collect metrics from the broker.

        Returns:
            Iterator of Prometheus metrics
        """
        # Metric to indicate broker is down
        celery_queue_up_metric = GaugeMetricFamily(
            "celery_queue_up",
            "Whether the broker connection is up",
            labels=["broker_type", "host", "port"],
        )
        # Queue length metric
        celery_queue_length_metric = GaugeMetricFamily(
            "celery_queue_length",
            "Number of messages in the queue",
            labels=["queue", "broker_type"],
        )
        # Queue consumer count metric
        celery_queue_consumer_metric = GaugeMetricFamily(
            "celery_queue_consumers",
            "Number of consumers for the queue",
            labels=["queue", "broker_type"],
        )
        # Queue memory usage metric (Redis only)
        celery_queue_memory_metric = GaugeMetricFamily(
            "celery_queue_memory_bytes",
            "Memory usage of the queue in bytes",
            labels=["queue", "broker_type"],
        )
        if not self._broker or not self._broker.is_connected():
            try:
                self._broker.connect()
            except Exception as e:
                logger.error(f"Failed to reconnect to broker: {e}")
                celery_queue_up_metric.add_metric(
                    labels=[
                        self._broker.connection_info["type"],
                        str(self._broker.connection_info["host"]),
                        str(self._broker.connection_info["port"]),
                    ],
                    value=0.0,
                )
                yield celery_queue_up_metric
                return

        celery_queue_up_metric.add_metric(
            labels=[
                self._broker.connection_info["type"],
                str(self._broker.connection_info["host"]),
                str(self._broker.connection_info["port"]),
            ],
            value=1.0,
        )
        yield celery_queue_up_metric

        try:
            # Get list of all queues
            queues = self._broker.list_queues()

            # Collect metrics for each queue
            for queue in queues:
                try:
                    metrics = self._broker.get_queue_metrics(queue)
                    broker_type = metrics["type"]

                    # Queue length
                    celery_queue_length_metric.add_metric(
                        labels=[queue, broker_type],
                        value=metrics["message_count"],
                    )

                    # Consumer count (if available)
                    if "consumer_count" in metrics:
                        celery_queue_consumer_metric.add_metric(
                            labels=[queue, broker_type],
                            value=metrics["consumer_count"],
                        )

                    # Memory usage (Redis only)
                    if "memory_bytes" in metrics:
                        celery_queue_memory_metric.add_metric(
                            labels=[queue, broker_type],
                            value=metrics["memory_bytes"],
                        )

                except Exception as e:
                    logger.error(f"Error collecting metrics for queue {queue}: {e}")
                    continue

            yield celery_queue_length_metric
            yield celery_queue_consumer_metric
            yield celery_queue_memory_metric

        except Exception as e:
            logger.error(f"Error collecting queue metrics: {e}")
