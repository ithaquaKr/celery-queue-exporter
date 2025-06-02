# Celery Queue Exporter

A Prometheus exporter for monitoring Celery queue metrics. This exporter provides real-time metrics about your Celery task queues, including queue lengths, task processing rates, and worker status.

## Features

- Real-time monitoring of Celery queue metrics
- Prometheus metrics export
- FastAPI-based HTTP endpoint
- Configurable logging
- Support for multiple Celery brokers

## Requirements

- Python 3.9 or higher
- Celery 5.3.0 or higher
- Prometheus client
- FastAPI and Uvicorn for the HTTP server

## Installation

```bash
# Using pip
pip install celery-queue-exporter

# Using uv (recommended)
uv pip install celery-queue-exporter
```

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ithalab/celery-queue-exporter.git
   cd celery-queue-exporter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Usage

Basic usage example:

```python
from celery_queue_exporter import CeleryQueueExporter

exporter = CeleryQueueExporter(
    broker_url="redis://localhost:6379/0",
    metrics_port=9808
)
exporter.start()
```

## Configuration

The exporter can be configured through environment variables:

- `CELERY_BROKER_URL`: The URL of your Celery broker
- `METRICS_PORT`: The port to expose Prometheus metrics (default: 9808)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file path (default: celery_queue_exporter.log)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
