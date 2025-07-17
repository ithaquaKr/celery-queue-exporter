import argparse
import logging

from prometheus_client.core import REGISTRY

from exporter.collector import CQCollector
from exporter.configs import (
    DefaultConfig,
    Settings,
)
from exporter.exporter import Exporter

logger = logging.getLogger(__package__)


def get_settings() -> Settings:
    parser = argparse.ArgumentParser(
        description="Celery Queue Exporter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host", type=str, default=DefaultConfig.HOST, help="Host to serve metrics on"
    )
    parser.add_argument(
        "--port", type=int, default=DefaultConfig.PORT, help="Port to serve metrics on"
    )
    parser.add_argument(
        "--polling-interval",
        type=int,
        default=DefaultConfig.POLLING_INTERVAL,
        help="Polling interval for collecting metrics",
    )
    parser.add_argument(
        "--monitor-queues",
        type=str,
        default=DefaultConfig.MONITOR_QUEUES,
        help="Queues to monitor, e.g. '0:celery;1:tasks'",
    )
    parser.add_argument(
        "--log-level", type=str, default=DefaultConfig.LOG_LEVEL, help="Log level"
    )
    parser.add_argument(
        "--log-format", type=str, default=DefaultConfig.LOG_FORMAT, help="Log format"
    )
    parser.add_argument(
        "--log-datefmt",
        type=str,
        default=DefaultConfig.LOG_DATEFMT,
        help="Log date format",
    )
    parser.add_argument(
        "--broker-type",
        type=str,
        default=DefaultConfig.BROKER_TYPE,
        help="Broker type (redis or rabbitmq)",
    )
    parser.add_argument(
        "--broker-host", type=str, default=DefaultConfig.BROKER_HOST, help="Broker host"
    )
    parser.add_argument(
        "--broker-port", type=int, default=DefaultConfig.BROKER_PORT, help="Broker port"
    )
    parser.add_argument(
        "--broker-password",
        type=str,
        default=DefaultConfig.BROKER_PASSWORD,
        help="Broker password",
    )
    parser.add_argument(
        "--broker-socket-timeout",
        type=float,
        default=DefaultConfig.BROKER_SOCKET_TIMEOUT,
        help="Broker socket timeout in seconds",
    )
    parser.add_argument(
        "--broker-use-sentinel",
        action="store_true",
        help="Use Redis Sentinel for broker",
    )
    parser.add_argument(
        "--broker-sentinel-hosts",
        type=str,
        default=DefaultConfig.BROKER_SENTINEL_HOSTS,
        help="Redis Sentinel hosts, e.g. 'host1:port1,host2:port2'",
    )
    parser.add_argument(
        "--broker-sentinel-master-name",
        type=str,
        default=DefaultConfig.BROKER_SENTINEL_MASTER_NAME,
        help="Redis Sentinel master name",
    )
    parser.add_argument(
        "--broker-sentinel-password",
        type=str,
        default=DefaultConfig.BROKER_SENTINEL_PASSWORD,
        help="Redis Sentinel password",
    )
    args = parser.parse_args()

    return Settings(
        **{k: v for k, v in vars(args).items()},
    )


def setup_logging(log_level: str, log_format: str, log_datefmt: str) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=log_datefmt,
    )


def run_exporter(settings: Settings) -> None:
    """Run the exporter."""
    setup_logging(settings.log_level, settings.log_format, settings.log_datefmt)
    logger.info("Exporter is starting ...")

    broker_config = {
        "host": settings.broker_host,
        "port": settings.broker_port,
        "password": settings.broker_password,
        "socket_timeout": settings.broker_socket_timeout,
        "use_sentinel": settings.broker_use_sentinel,
        "sentinel_hosts": settings.broker_sentinel_hosts,
        "sentinel_master_name": settings.broker_sentinel_master_name,
        "sentinel_password": settings.broker_sentinel_password,
    }

    REGISTRY.register(
        CQCollector(
            broker_type=settings.broker_type,
            broker_config=broker_config,
            monitor_queues_config=settings.monitor_queues,
        )
    )
    Exporter(
        REGISTRY,
        settings.polling_interval,
    ).serve_metrics(settings.host, settings.port)


def main():
    settings = get_settings()
    run_exporter(settings)


if __name__ == "__main__":
    main()
