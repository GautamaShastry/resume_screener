import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    status: str
    progress: dict
    result_ref: dict | None
    error_code: str | None
    error_message: str | None
    created_at: datetime


class TaskStarted(BaseModel):
    task_id: uuid.UUID
