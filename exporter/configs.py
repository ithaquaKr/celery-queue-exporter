"""
Configurations.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


# Default values
class DefaultConfig:
    HOST = "0.0.0.0"
    PORT = 9726
    POLLING_INTERVAL = 30
    MONITOR_QUEUES = "0:celery"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"
    BROKER_TYPE = "redis"
    BROKER_HOST = "localhost"
    BROKER_PORT = 6379
    BROKER_PASSWORD = None
    BROKER_SOCKET_TIMEOUT = 5.0
    BROKER_USE_SENTINEL = False
    BROKER_SENTINEL_HOSTS = None
    BROKER_SENTINEL_MASTER_NAME = None
    BROKER_SENTINEL_PASSWORD = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="cq_exporter_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    host: str
    port: int
    polling_interval: int
    monitor_queues: str
    log_level: str
    log_format: str
    log_datefmt: str
    broker_type: str
    broker_host: str
    broker_port: int
    broker_password: Optional[str] = None
    broker_socket_timeout: float
    broker_use_sentinel: bool
    broker_sentinel_hosts: Optional[str] = None
    broker_sentinel_master_name: Optional[str] = None
    broker_sentinel_password: Optional[str] = None
