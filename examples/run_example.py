"""Script to run the example application and submit tasks."""

import random
import time
from typing import Any, Dict, List, Optional

from celery import Celery, Task
from celery.signals import task_failure

# Create Celery app with configuration
app = Celery("example_app")

# Configure Celery with multiple queues and other settings
app.conf.update(
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "high_priority": {"exchange": "high_priority", "routing_key": "high_priority"},
        "low_priority": {"exchange": "low_priority", "routing_key": "low_priority"},
    },
    task_routes={
        "examples.tasks.process_data": {"queue": "high_priority"},
        "examples.tasks.background_task": {"queue": "low_priority"},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    enable_utc=True,
    task_track_started=True,
)


class BaseTask(Task):
    """Base task class with retry behavior."""

    max_retries = 3
    default_retry_delay = 5

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        print(f"Task {task_id} failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Global task failure handler."""
    print(f"Task {task_id} failed with exception: {exception}")


@app.task(base=BaseTask, queue="high_priority")
def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process data with high priority."""
    time.sleep(2)  # Simulate processing
    return {"processed_items": len(data), "status": "completed"}


@app.task(base=BaseTask, queue="low_priority")
def background_task(task_name: str) -> str:
    """Execute a background task with low priority."""
    time.sleep(5)  # Simulate long-running task
    return f"Completed {task_name}"


@app.task(bind=True, queue="default")
def retry_task(self, value: int) -> Optional[int]:
    """Task demonstrating retry mechanism."""
    try:
        if value < 0:
            raise ValueError("Value must be non-negative")
        time.sleep(1)
        return value * 2
    except ValueError as exc:
        return self.retry(exc=exc)


@app.task(queue="high_priority")
def error_task() -> None:
    """Task that always fails for testing error handling."""
    raise RuntimeError("This task always fails")


def main():
    """Run the example application."""
    print("Starting example application...")
    print(
        "This will submit various tasks to demonstrate the Celery Queue Exporter functionality"
    )

    # Submit tasks continuously
    task_count = 0
    try:
        while True:
            # Submit a mix of tasks
            if task_count % 5 == 0:
                # High priority task
                data = [{"id": i} for i in range(random.randint(1, 5))]
                process_data.delay(data)
                print(f"Submitted high priority task to process {len(data)} items")

            if task_count % 3 == 0:
                # Low priority task
                background_task.delay(f"background_task_{task_count}")
                print(f"Submitted low priority background task {task_count}")

            if task_count % 7 == 0:
                # Task that might retry
                value = random.randint(-2, 5)
                retry_task.delay(value)
                print(f"Submitted retry task with value {value}")

            if task_count % 11 == 0:
                # Error task
                error_task.delay()
                print("Submitted error task")

            task_count += 1
            time.sleep(2)  # Wait between task submissions

    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
