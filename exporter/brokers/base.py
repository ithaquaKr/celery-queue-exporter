"""Base classes for brokers."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Broker(ABC):
    """Abstract interface for Celery broker implementations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the broker."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection to the broker."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the connection to the broker is active."""
        pass

    @abstractmethod
    def ping(self) -> bool:
        """Check if broker is reachable."""
        pass

    @property
    @abstractmethod
    def connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        pass

    @abstractmethod
    def get_queue_length(self, queue_name: str) -> int:
        """Get the number of messages in a queue.

        Args:
            queue_name: Name of the queue to inspect

        Returns:
            Number of messages in the queue
        """
        pass

    @abstractmethod
    def get_queue_tasks(self, queue_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a queue.

        Args:
            queue_name: Name of the queue to inspect
        """
        pass

    @abstractmethod
    def list_queues(self) -> list[str]:
        """Get list of all queue names.

        Returns:
            List of queue names
        """
        pass
