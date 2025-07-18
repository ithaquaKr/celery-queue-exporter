import os

from celery import Celery

# Check if we should use Redis Sentinel
USE_SENTINEL = os.getenv("REDIS_USE_SENTINEL", "false").lower() in ("true", "1", "yes")

if USE_SENTINEL:
    # Redis Sentinel configuration
    sentinel_hosts = os.getenv("REDIS_SENTINEL_HOSTS", "localhost:26379")
    master_name = os.getenv("REDIS_SENTINEL_MASTER_NAME", "mymaster")
    redis_db = os.getenv("REDIS_DB", "0")

    # Format for sentinel URL is sentinel://host:port;host2:port2/...
    broker_url = f"sentinel://{sentinel_hosts.replace(',', ';')}/{redis_db}"
    backend_url = broker_url

    celery_app = Celery(
        "task_manager",
        broker=broker_url,
        backend=backend_url,
        include=["app.tasks"],
    )

    celery_app.conf.broker_transport_options = {"master_name": master_name}
    celery_app.conf.result_backend_transport_options = {"master_name": master_name}

else:
    # Standard Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_app = Celery(
        "task_manager", broker=REDIS_URL, backend=REDIS_URL, include=["app.tasks"]
    )

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    task_routes={
        "celery.*": {"queue": "celery"},
        "mail.*": {"queue": "mail"},
    },
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_send_task_events=True,
    task_send_sent_event=True,
)
