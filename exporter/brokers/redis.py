import logging
from typing import Any, Dict, Optional, List

import redis
from redis.exceptions import RedisError
from redis.sentinel import Sentinel

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
        use_sentinel: bool = False,
        sentinel_hosts: Optional[str] = None,
        sentinel_master_name: Optional[str] = None,
        sentinel_password: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize Redis broker connection.

        Args:
            host: Redis host address
            port: Redis port number
            db: Redis database number
            password: Optional Redis password
            socket_timeout: Socket timeout in seconds
            use_sentinel: Use Redis Sentinel for connection
            sentinel_hosts: Comma-separated list of Sentinel hosts
            sentinel_master_name: Name of the master to monitor
            sentinel_password: Optional Sentinel password
            **kwargs: Additional redis-py connection arguments
        """
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._socket_timeout = socket_timeout
        self._use_sentinel = use_sentinel
        self._sentinel_hosts = sentinel_hosts
        self._sentinel_master_name = sentinel_master_name
        self._sentinel_password = sentinel_password
        self._kwargs = kwargs
        self._client: Optional[redis.Redis] = None

    def _get_sentinel_connection(self) -> redis.Redis:
        """Get a connection to the master from a Sentinel."""
        if not self._sentinel_hosts:
            raise ValueError("Sentinel hosts must be provided")
        if not self._sentinel_master_name:
            raise ValueError("Sentinel master name must be provided")

        sentinel_hosts: List[Any] = [
            tuple(host.split(":")) for host in self._sentinel_hosts.split(",")
        ]
        sentinel = Sentinel(
            sentinels=sentinel_hosts,
            password=self._sentinel_password,
            socket_timeout=self._socket_timeout,
            **self._kwargs,
        )
        return sentinel.master_for(
            self._sentinel_master_name,
            db=self._db,
            password=self._password,
            socket_timeout=self._socket_timeout,
            **self._kwargs,
        )

    def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            if self._use_sentinel:
                self._client = self._get_sentinel_connection()
            else:
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
            logger.info(f"Connected to Redis at {self.connection_info}")
        except (RedisError, ValueError) as e:
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
        if self._use_sentinel:
            return {
                "sentinel_hosts": self._sentinel_hosts,
                "sentinel_master_name": self._sentinel_master_name,
                "vdb": self._db,
                "type": "redis-sentinel",
            }
        return {
            "host": self._host,
            "port": self._port,
            "vdb": self._db,
            "type": "redis",
        }
