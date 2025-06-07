import os

from celery import Celery

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery instance
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
)
