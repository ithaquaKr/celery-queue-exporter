"""Test configuration and fixtures for celery-queue-exporter."""

import pytest
from celery import Celery


@pytest.fixture
def celery_app():
    """Create a Celery application for testing."""
    app = Celery(
        "test_app",
        broker="memory://",
        backend="memory://",
    )
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        task_store_eager_result=True,
    )
    return app


@pytest.fixture
def celery_config():
    """Return a test configuration for Celery."""
    return {
        "broker_url": "memory://",
        "result_backend": "memory://",
        "task_always_eager": True,
        "task_eager_propagates": True,
        "task_store_eager_result": True,
    }
