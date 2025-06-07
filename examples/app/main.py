import logging

from fastapi import FastAPI, HTTPException

from app.celery import celery_app
from app.models import (
    EmailRequest,
    ProcessDataRequest,
    TaskResponse,
    TaskStatus,
    TaskStatusResponse,
)
from app.tasks import process_data_task, send_email_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="A FastAPI application with Celery background tasks for data processing, email sending, and external API calls",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", summary="Health Check")
async def root():
    """Root endpoint for health checking"""
    return {"message": "Task Manager API is running", "status": "healthy"}


@app.post(
    "/tasks/process-data",
    response_model=TaskResponse,
    summary="Start Data Processing Task",
)
async def start_data_processing(request: ProcessDataRequest):
    """
    Start a background data processing task

    This task simulates processing multiple items with progress updates.
    Each item takes a specified amount of time to process.
    """
    try:
        task = process_data_task.delay(
            {
                "item_count": request.item_count,
                "processing_time": request.processing_time,
            }
        )

        logger.info(f"Started data processing task: {task.id}")

        return TaskResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            message=f"Data processing task started. Processing {request.item_count} items.",
        )
    except Exception as e:
        logger.error(f"Failed to start data processing task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@app.post(
    "/tasks/send-email", response_model=TaskResponse, summary="Start Email Sending Task"
)
async def start_email_sending(request: EmailRequest):
    """
    Start a background email sending task

    This task simulates sending an email with potential random failures.
    """
    try:
        task = send_email_task.delay(
            {
                "to": request.to,
                "subject": request.subject,
                "body": request.body,
                "processing_time": request.processing_time,
            }
        )

        logger.info(f"Started email sending task: {task.id}")

        return TaskResponse(
            task_id=task.id,
            status=TaskStatus.PENDING,
            message=f"Email sending task started for {request.to}",
        )
    except Exception as e:
        logger.error(f"Failed to start email task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@app.get(
    "/tasks/{task_id}/status",
    response_model=TaskStatusResponse,
    summary="Get Task Status",
)
async def get_task_status(task_id: str):
    """
    Get the status and result of a specific task

    Returns the current status, progress information, and results (if completed).
    """
    try:
        task_result = celery_app.AsyncResult(task_id)

        if task_result.state == "PENDING":
            response = TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.PENDING,
                meta={"message": "Task is waiting to be processed"},
            )
        elif task_result.state == "PROGRESS":
            response = TaskStatusResponse(
                task_id=task_id, status=TaskStatus.PROGRESS, meta=task_result.info
            )
        elif task_result.state == "SUCCESS":
            response = TaskStatusResponse(
                task_id=task_id, status=TaskStatus.SUCCESS, result=task_result.result
            )
        elif task_result.state == "FAILURE":
            response = TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus.FAILURE,
                error=str(task_result.info),
                meta={"traceback": task_result.traceback},
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=TaskStatus(task_result.state),
                meta={"raw_state": task_result.state},
            )

        return response

    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get task status: {str(e)}"
        )


@app.delete("/tasks/{task_id}", summary="Cancel Task")
async def cancel_task(task_id: str):
    """
    Cancel a running or pending task
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)

        return {
            "task_id": task_id,
            "message": "Task cancellation requested",
            "status": "revoked",
        }
    except Exception as e:
        logger.error(f"Failed to cancel task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@app.get("/tasks", summary="List Active Tasks")
async def list_active_tasks():
    """
    Get information about currently active tasks
    """
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()

        return {
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "total_active": sum(len(tasks) for tasks in (active_tasks or {}).values()),
            "total_scheduled": sum(
                len(tasks) for tasks in (scheduled_tasks or {}).values()
            ),
        }
    except Exception as e:
        logger.error(f"Failed to list tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@app.get("/workers", summary="Get Worker Information")
async def get_worker_info():
    """
    Get information about available Celery workers
    """
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()

        if not stats:
            return {
                "workers": [],
                "total_workers": 0,
                "message": "No workers available",
            }

        worker_info = []
        for worker_name, worker_stats in stats.items():
            worker_info.append(
                {
                    "name": worker_name,
                    "status": "online",
                    "processed_tasks": worker_stats.get("total", {}),
                    "active_tasks": len(inspect.active().get(worker_name, [])),
                    "load": worker_stats.get("rusage", {}),
                }
            )

        return {"workers": worker_info, "total_workers": len(worker_info)}
    except Exception as e:
        logger.error(f"Failed to get worker info: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get worker info: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
