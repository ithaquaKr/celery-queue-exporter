import logging
from typing import Any, Dict, Optional

import redis
from redis.exceptions import RedisError

from exporter.brokers.base import Broker

logger = logging.getLogger(__name__)


class RedisBroker(Broker):
    """Redis broker implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: float = 5.0,
        **kwargs,
    ) -> None:
        """Initialize Redis broker connection.

        Args:
            host: Redis host address
            port: Redis port number
            db: Redis database number
            password: Optional Redis password
            socket_timeout: Socket timeout in seconds
            **kwargs: Additional redis-py connection arguments
        """
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._socket_timeout = socket_timeout
        self._kwargs = kwargs
        self._client: Optional[redis.Redis] = None

    def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                socket_timeout=self._socket_timeout,
                **self._kwargs,
            )
            # Test connection
            self._client.ping()
            logger.info(f"Connected to Redis at {self._host}:{self._port}/db{self._db}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None
            raise

    def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Disconnected from Redis")
            except RedisError as e:
                logger.error(f"Error disconnecting from Redis: {e}")
            finally:
                self._client = None

    def is_connected(self) -> bool:
        """Check if Redis connection is active."""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except RedisError:
            return False

    def get_queue_length(self, queue_name: str) -> int:
        """Get number of messages in a Redis queue.

        Args:
            queue_name: Name of the queue to inspect

        Returns:
            Number of messages in queue

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RuntimeError("Not connected to Redis")

        try:
            # In Redis, Celery queues are stored as lists
            return self._client.llen(queue_name)
        except RedisError as e:
            logger.error(f"Failed to get queue length for {queue_name}: {e}")
            raise

    def get_queue_tasks(self, queue_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a Redis queue.

        Args:
            queue_name: Name of the queue to inspect

        Returns:
            Dictionary containing queue metrics

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RuntimeError("Not connected to Redis")

        try:
            # Get basic queue stats
            length = self.get_queue_length(queue_name)

            # Get memory usage if available (Redis >= 4.0)
            try:
                memory = self._client.memory_usage(queue_name) or 0
            except RedisError:
                memory = 0

            return {
                "message_count": length,
                "memory_bytes": memory,
                "consumers": -1,  # Redis doesn't track consumers directly
                "type": "redis",
            }
        except RedisError as e:
            logger.error(f"Failed to get metrics for queue {queue_name}: {e}")
            raise

    def list_queues(self) -> list[str]:
        """Get list of all queue names in Redis.

        Returns:
            List of queue names

        Raises:
            RedisError: If Redis operation fails
        """
        if not self._client:
            raise RuntimeError("Not connected to Redis")

        try:
            # Celery queue keys match pattern: celery:*
            keys = self._client.keys("celery:*")
            return [key.decode() for key in keys]
        except RedisError:
            logger.error("Failed to list queues: {e}")
            raise

    def ping(self) -> bool:
        """Check if Redis is reachable.

        Returns:
            True if Redis responds to ping, False otherwise
        """
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except RedisError:
            return False

    @property
    def connection_info(self) -> Dict[str, Any]:
        """Get Redis connection information.

        Returns:
            Dictionary with connection details
        """
        return {
            "host": self._host,
            "port": self._port,
            "db": self._db,
            "type": "redis",
        }
