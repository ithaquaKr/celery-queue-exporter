# Celery Queue Exporter

[![CI](https://github.com/ithaquaKr/celery-queue-exporter/actions/workflows/ci.yml/badge.svg)](https://github.com/ithaquaKr/celery-queue-exporter/actions/workflows/ci.yml)
A Prometheus exporter for monitoring Celery queue.

## Features

> TBD

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
