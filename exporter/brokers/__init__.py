"""Broker implementations for Celery queue exporter."""

from typing import Dict, Type

from exporter.brokers.base import Broker
from exporter.brokers.redis import RedisBroker

# from exporter.brokers.rabbitmq import RabbitMQBroker


__all__ = [
    "Broker",
    "RedisBroker",
    # "RabbitMQBroker",
    "BrokerFactory",
]


class BrokerFactory:
    """Factory class for creating broker instances."""

    # Registry of supported broker types
    _broker_types: Dict[str, Type[Broker]] = {
        "redis": RedisBroker,
        # "rabbitmq": RabbitMQBroker,
    }

    @classmethod
    def create(cls, broker_type: str, **kwargs) -> Broker:
        """Create a new broker instance.

        Args:
            broker_type: Type of broker to create
            **kwargs: Configuration parameters for the broker

        Returns:
            Configured broker instance

        Raises:
            ValueError: If broker_type is not supported
        """
        broker_class = cls._broker_types.get(broker_type.lower())
        if not broker_class:
            raise ValueError(
                f"Unsupported broker type: {broker_type}. "
                f"Supported types: {list(cls._broker_types.keys())}"
            )

        return broker_class(**kwargs)
