"""Basic usage example for the Celery Queue Exporter."""

import os
import time
from celery import Celery
from celery_queue_exporter import CeleryQueueExporter

# Create a Celery app for demonstration
app = Celery(
    "example_app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
)


@app.task
def add(x: int, y: int) -> int:
    """Example task that adds two numbers."""
    time.sleep(1)  # Simulate some work
    return x + y


def main():
    """Run the example."""
    # Create and start the exporter
    exporter = CeleryQueueExporter(
        broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        metrics_port=int(os.getenv("METRICS_PORT", "9808")),
    )
    exporter.start()

    # Submit some example tasks
    for i in range(5):
        add.delay(i, i + 1)
        time.sleep(0.5)

    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
