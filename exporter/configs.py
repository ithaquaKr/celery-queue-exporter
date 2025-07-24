"""
Settings for the Celery Queue Exporter.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="cq_exporter_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    host: str = "0.0.0.0"
    port: int = 9726
    polling_interval: int = 30
    monitor_queues: str = "0:celery"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_datefmt: str = "%Y-%m-%d %H:%M:%S"
    broker_type: str = "redis"
    broker_host: str = "localhost"
    broker_port: int = 6379
    broker_password: Optional[str] = None
    broker_socket_timeout: float = 5.0
    broker_use_sentinel: bool = False
    broker_sentinel_hosts: Optional[str] = None
    broker_sentinel_master_name: Optional[str] = None
    broker_sentinel_password: Optional[str] = None
