import logging
from typing import Dict, Any, Optional
import pika
from pika.exceptions import AMQPError

from exporter.brokers import Broker


logger = logging.getLogger(__name__)


class RabbitMQBroker(Broker):
    """RabbitMQ broker implementation."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        username: str = "guest",
        password: str = "guest",
        **kwargs,
    ) -> None:
        """Initialize RabbitMQ broker connection.

        Args:
            host: RabbitMQ host address
            port: RabbitMQ port number
            virtual_host: RabbitMQ virtual host
            username: RabbitMQ username
            password: RabbitMQ password
            **kwargs: Additional pika connection arguments
        """
        self._host = host
        self._port = port
        self._virtual_host = virtual_host
        self._username = username
        self._password = password
        self._kwargs = kwargs
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None

    def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(
                username=self._username, password=self._password
            )
            parameters = pika.ConnectionParameters(
                host=self._host,
                port=self._port,
                virtual_host=self._virtual_host,
                credentials=credentials,
                **self._kwargs,
            )
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()
            logger.info(
                f"Connected to RabbitMQ at {self._host}:{self._port}"
                f" vhost={self._virtual_host}"
            )
        except AMQPError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self._connection = None
            self._channel = None
            raise

    def disconnect(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection:
            try:
                self._connection.close()
                logger.info("Disconnected from RabbitMQ")
            except AMQPError as e:
                logger.error(f"Error disconnecting from RabbitMQ: {e}")
            finally:
                self._connection = None
                self._channel = None

    def is_connected(self) -> bool:
        """Check if RabbitMQ connection is active."""
        return (
            self._connection is not None
            and not self._connection.is_closed
            and self._channel is not None
            and not self._channel.is_closed
        )

    def get_queue_length(self, queue_name: str) -> int:
        """Get number of messages in a RabbitMQ queue.

        Args:
            queue_name: Name of the queue to inspect

        Returns:
            Number of messages in queue

        Raises:
            AMQPError: If RabbitMQ operation fails
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to RabbitMQ")

        try:
            # Declare queue passively (don't create if doesn't exist)
            response = self._channel.queue_declare(queue=queue_name, passive=True)
            return response.method.message_count
        except AMQPError as e:
            logger.error(f"Failed to get queue length for {queue_name}: {e}")
            raise

    def get_queue_metrics(self, queue_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a RabbitMQ queue.

        Args:
            queue_name: Name of the queue to inspect

        Returns:
            Dictionary containing queue metrics

        Raises:
            AMQPError: If RabbitMQ operation fails
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to RabbitMQ")

        try:
            # Get queue stats
            response = self._channel.queue_declare(queue=queue_name, passive=True)

            return {
                "message_count": response.method.message_count,
                "consumer_count": response.method.consumer_count,
                "type": "rabbitmq",
            }
        except AMQPError as e:
            logger.error(f"Failed to get metrics for queue {queue_name}: {e}")
            raise

    def list_queues(self) -> list[str]:
        """Get list of all queue names in RabbitMQ.

        Returns:
            List of queue names

        Raises:
            AMQPError: If RabbitMQ operation fails
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to RabbitMQ")

        try:
            # List all queues in the virtual host
            return [
                queue.method.queue
                for queue in self._channel.queue_declare(
                    queue="", exclusive=True
                ).method.queue
            ]
        except AMQPError as e:
            logger.error(f"Failed to list queues: {e}")
            raise

    def ping(self) -> bool:
        """Check if RabbitMQ is reachable.

        Returns:
            True if RabbitMQ responds, False otherwise
        """
        if not self._connection:
            return False
        try:
            return not self._connection.is_closed
        except AMQPError:
            return False

    @property
    def connection_info(self) -> Dict[str, Any]:
        """Get RabbitMQ connection information.

        Returns:
            Dictionary with connection details
        """
        return {
            "host": self._host,
            "port": self._port,
            "virtual_host": self._virtual_host,
            "type": "rabbitmq",
        }
