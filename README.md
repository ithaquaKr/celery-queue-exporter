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

## Troubleshoot

### Bug

```python
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/app/exporter/__main__.py", line 128, in <module>
    main()
  File "/app/exporter/__main__.py", line 124, in main
    run_exporter(settings)
  File "/app/exporter/__main__.py", line 119, in run_exporter
    ).serve_metrics(settings.host, settings.port)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/exporter/exporter.py", line 112, in serve_metrics
    self._http_server = HTTPServer((host, port), MetricsHandler)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/socketserver.py", line 457, in __init__
    self.server_bind()
  File "/usr/local/lib/python3.12/http/server.py", line 136, in server_bind
    socketserver.TCPServer.server_bind(self)
  File "/usr/local/lib/python3.12/socketserver.py", line 478, in server_bind
    self.socket.bind(self.server_address)
socket.gaierror: [Errno -2] Name does not resolve
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
