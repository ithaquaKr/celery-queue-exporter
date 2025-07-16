import logging
from typing import Any, Dict, Iterable, List, Optional

from prometheus_client import Metric
from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from exporter.brokers import Broker, BrokerFactory
from exporter.utils import parse_monitor_queues

logger = logging.getLogger(__name__)


class CQCollector(Collector):
    """Celery Queue metrics collector for Prometheus."""

    def __init__(
        self,
        broker_type: str,
        broker_config: Dict[str, Any],
        monitor_queues_config: str,
    ) -> None:
        """Initialize the collector.

        Args:
            broker_type: Type of broker to use
            broker_config: Configuration for the broker connection
            monitor_queues_config: Configuration for the queues to monitor
        """
        self._monitor_queues: Dict[int, List[str]] = parse_monitor_queues(
            monitor_queues_config
        )
        self._broker_type: str = broker_type
        self._brokers: Dict[int, Optional[Broker]] = {}
        for db, _ in self._monitor_queues.items():
            try:
                broker_config["db"] = db
                broker = BrokerFactory.create(broker_type, **broker_config)
                broker.connect()
                self._brokers[db] = broker
            except Exception as e:
                logger.error(
                    f"Failed to initialize broker for db {db}: {e}", exc_info=True
                )
                raise

    def collect(self) -> Iterable[Metric]:
        """Collect metrics from the broker.

        Returns:
            Iterator of Prometheus metrics
        """
        # Queue length metric
        celery_queue_length_metric = GaugeMetricFamily(
            "celery_queue_length",
            "Number of key in the queue",
            labels=["broker_type", "queue", "vdb"],
        )

        try:
            # Collect metrics for each db
            for db, queues in self._monitor_queues.items():
                broker = self._brokers.get(db)
                if not broker:
                    continue
                # Get list of all queues
                # Collect metrics for each queue
                for queue in queues:
                    try:
                        length = broker.get_queue_length(queue)

                        # Queue length
                        celery_queue_length_metric.add_metric(
                            labels=[self._broker_type, queue, str(db)],
                            value=length,
                        )

                    except Exception as e:
                        logger.error(
                            f"Error collecting metrics for queue {queue} in db {db}: {e}"
                        )
                        continue

            yield celery_queue_length_metric

        except Exception as e:
            logger.error(f"Error collecting queue metrics: {e}")
