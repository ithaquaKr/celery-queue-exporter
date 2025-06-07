# FastAPI + Celery Task Management System

This is a comprehensive example of a FastAPI application with Celery background tasks. The application demonstrates real-world usage patterns including data processing, email sending simulation, and external API calls.

## Project Structure

```
examples/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── celery_app.py    # Celery configuration
│   ├── tasks.py         # Background tasks
│   └── models.py        # Pydantic models
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker setup
├── Dockerfile           # Dockerfile to build
└── README.md            # This file
```

## Prerequisites

- Python 3.8+
- Redis server
- pip or poetry for package management

## Installation & Setup

### 1. Clone and Setup Python Environment

```bash
# Create project directory
mkdir task_manager
cd task_manager

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install and Start Redis

**Using Docker**

```bash
docker run -d -p 6379:6379 --name redis-server redis:7.4-alpine
```

**Verify Redis is running:**

```bash
redis-cli ping
# Should return: PONG
```

## Running the Application

You need to run **two separate processes**:

### Terminal 1: Start the FastAPI Server

```bash
# From project root directory
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

### Terminal 2: Start the Celery Worker

```bash
# From project root directory
celery -A app.celery worker --loglevel=info
```

## Testing the Application

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Using Swagger UI

1. Open <http://localhost:8000/docs> in your browser
2. Try the different endpoints:
    - **POST /tasks/process-data**: Process multiple items with progress tracking
    - **POST /tasks/send-email**: Simulate email sending
    - **POST /tasks/fetch-data**: Fetch data from external API
    - **GET /tasks/{task_id}/status**: Check task status and results

## Task Types Explained

### 1. Data Processing Task (`/tasks/process-data`)

- Simulates processing multiple items
- Provides real-time progress updates
- Configurable item count and processing time
- Returns statistical summary of processed data

### 2. Email Sending Task (`/tasks/send-email`)

- Simulates sending emails
- Has 10% random failure rate to demonstrate error handling
- Returns delivery confirmation with message ID

## Docker

Run with Docker:

```bash
docker-compose up
```
