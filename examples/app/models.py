from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"


class ProcessDataRequest(BaseModel):
    item_count: int = Field(
        default=5, ge=1, le=50, description="Number of items to process"
    )
    processing_time: float = Field(
        default=1.0, ge=0.1, le=100.0, description="Processing time per item in seconds"
    )


class EmailRequest(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., max_length=200, description="Email subject")
    body: str = Field(..., max_length=5000, description="Email body")
    processing_time: float = Field(
        default=1.0, ge=0.1, le=100.0, description="Processing time in seconds"
    )


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
